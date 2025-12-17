"""
Logical plan construction from parsed SQL AST.
"""

from dataclasses import dataclass, field
from sqlglot import expressions as exp
from .parser import ParseError


@dataclass
class JoinInfo:
    """Information about a single join."""
    table: str
    alias: object
    join_type: str  # "INNER" or "LEFT"
    left_key: str  # e.g., "sp.fk_abs"
    right_key: str  # e.g., "spa.id"
    additional_where: object = None  # Additional WHERE conditions from ON clause


@dataclass
class LogicalPlan:
    """Logical execution plan for a query."""
    root_table: str
    root_alias: object
    joins: list
    where_expr: object
    projections: list  # SELECT expressions with aliases
    required_columns: dict = field(default_factory=dict)  # Table name -> set of column names (added by optimizer)
    pushable_where_expr: object = None  # WHERE conditions that can be pushed to root table


def build_logical_plan(ast, registered_tables):
    """
    Convert SQL AST into a logical plan.
    
    Args:
        ast: Parsed SELECT expression
        registered_tables: Set of registered table names
        
    Returns:
        LogicalPlan object
        
    Raises:
        ParseError: If plan construction fails
    """
    # Extract FROM clause
    # Note: sqlglot uses 'from_' (with underscore) to avoid Python keyword conflict
    from_expr = ast.args.get("from_") or ast.args.get("from")
    if not from_expr:
        raise ParseError("Query must have a FROM clause")
    
    root_table, root_alias = _extract_table_and_alias(from_expr.this)
    
    if root_table not in registered_tables:
        raise ParseError(f"Table '{root_table}' is not registered")
    
    # Extract JOINs
    joins = []
    additional_where_conditions = []
    for join_expr in ast.args.get("joins", []):
        join_info = _extract_join(join_expr, registered_tables)
        joins.append(join_info)
        # Collect additional WHERE conditions from JOIN ON clauses
        if join_info.additional_where is not None:
            additional_where_conditions.append(join_info.additional_where)
    
    # Extract WHERE clause
    where_expr = ast.args.get("where")
    # Unwrap Where node if present (sqlglot wraps WHERE expressions in a Where node)
    if where_expr is not None:
        if isinstance(where_expr, exp.Where):
            where_expr = where_expr.this
        # where_expr is now the actual expression (And, Or, EQ, etc.)
    
    # Merge additional WHERE conditions from JOIN ON clauses into main WHERE clause
    if additional_where_conditions:
        if where_expr is None:
            # No existing WHERE clause, use the first additional condition
            where_expr = additional_where_conditions[0]
            # Combine remaining conditions with AND
            for cond in additional_where_conditions[1:]:
                where_expr = exp.And(this=where_expr, expression=cond)
        else:
            # Combine existing WHERE with additional conditions using AND
            combined = where_expr
            for cond in additional_where_conditions:
                combined = exp.And(this=combined, expression=cond)
            where_expr = combined
    
    # Extract SELECT projections
    projections = list(ast.expressions)
    
    # Build initial plan
    plan = LogicalPlan(
        root_table=root_table,
        root_alias=root_alias,
        joins=joins,
        where_expr=where_expr,
        projections=projections
    )
    
    # Apply optimizations (column pruning and filter pushdown)
    from .optimizer import analyze_required_columns, analyze_filter_pushdown
    
    # Analyze required columns
    plan.required_columns = analyze_required_columns(plan)
    
    # Analyze filter pushdown
    pushable_where, remaining_where = analyze_filter_pushdown(plan)
    plan.pushable_where_expr = pushable_where
    plan.where_expr = remaining_where  # Update to only non-pushable conditions
    
    return plan
    
    
def _extract_table_and_alias(expr):
    """Extract table name and alias from a table expression."""
    if isinstance(expr, exp.Table):
        table_name = expr.name
        alias = expr.alias
        return table_name, alias
    elif isinstance(expr, exp.Alias):
        # Handle table with alias
        if isinstance(expr.this, exp.Table):
            return expr.this.name, expr.alias
        else:
            raise ParseError(f"Unsupported table expression: {type(expr.this)}")
    else:
        raise ParseError(f"Unsupported FROM expression: {type(expr)}")


def _extract_join(join_expr, registered_tables):
    """Extract join information from a JOIN expression."""
    # Determine join type
    join_type = "INNER"
    if join_expr.kind == "LEFT":
        join_type = "LEFT"
    elif join_expr.kind and join_expr.kind.upper() not in ("INNER", "LEFT"):
        raise ParseError(f"Unsupported join type: {join_expr.kind}")
    
    # Extract table and alias
    table, alias = _extract_table_and_alias(join_expr.this)
    
    if table not in registered_tables:
        raise ParseError(f"Table '{table}' in JOIN is not registered")
    
    # Extract join condition
    on_expr = join_expr.args.get("on")
    if not on_expr:
        raise ParseError("JOIN must have an ON condition")
    
    result = _extract_join_keys(on_expr)
    if len(result) == 3:
        left_key, right_key, additional_where = result
    else:
        # Backward compatibility: if function returns 2 values
        left_key, right_key = result
        additional_where = None
    
    join_info = JoinInfo(
        table=table,
        alias=alias,
        join_type=join_type,
        left_key=left_key,
        right_key=right_key
    )
    
    # Store additional WHERE conditions to be added later
    if additional_where is not None:
        join_info.additional_where = additional_where
    else:
        join_info.additional_where = None
    
    return join_info


def _extract_join_keys(on_expr):
    """
    Extract join keys from ON condition.
    Supports single equality joins: alias1.col1 = alias2.col2
    For multiple conditions with AND, uses the first equality condition as the join key
    and returns additional conditions to be moved to WHERE clause.
    """
    # Handle multiple conditions with AND
    if isinstance(on_expr, exp.And):
        # Extract all equality conditions
        equality_conditions = []
        other_conditions = []
        
        def _extract_conditions(expr):
            if isinstance(expr, exp.And):
                _extract_conditions(expr.this)
                _extract_conditions(expr.expression)
            elif isinstance(expr, exp.EQ):
                equality_conditions.append(expr)
            else:
                other_conditions.append(expr)
        
        _extract_conditions(on_expr)
        
        if not equality_conditions:
            raise ParseError("ON clause must contain at least one equality condition")
        
        # Use the first equality condition as the join key
        first_eq = equality_conditions[0]
        left = first_eq.this
        right = first_eq.expression
        
        left_key = _column_to_string(left)
        right_key = _column_to_string(right)
        
        # Combine remaining conditions to be added to WHERE clause
        remaining_conditions = equality_conditions[1:] + other_conditions
        additional_where = None
        if remaining_conditions:
            if len(remaining_conditions) == 1:
                additional_where = remaining_conditions[0]
            else:
                # Combine multiple conditions with AND
                additional_where = remaining_conditions[0]
                for cond in remaining_conditions[1:]:
                    additional_where = exp.And(this=additional_where, expression=cond)
        
        return left_key, right_key, additional_where
    
    # Handle single equality condition
    elif isinstance(on_expr, exp.EQ):
        left = on_expr.this
        right = on_expr.expression
        
        left_key = _column_to_string(left)
        right_key = _column_to_string(right)
        
        return left_key, right_key, None
    
    else:
        raise ParseError("Only equality joins are supported in ON clause")


def _column_to_string(expr):
    """Convert a column expression to string format 'alias.column'."""
    if isinstance(expr, exp.Column):
        table = expr.table
        column = expr.name
        if table:
            return f"{table}.{column}"
        else:
            raise ParseError(f"Column reference must include table alias: {expr}")
    else:
        raise ParseError(f"Join key must be a column reference, got {type(expr)}")

