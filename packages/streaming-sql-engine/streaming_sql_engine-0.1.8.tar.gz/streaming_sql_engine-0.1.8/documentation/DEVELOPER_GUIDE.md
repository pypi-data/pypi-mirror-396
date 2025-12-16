# Developer Guide: Streaming SQL Engine

This guide is for developers who want to understand, modify, or extend the Streaming SQL Engine codebase.

## Quick Start for Developers

### Prerequisites

- Python 3.8+
- Understanding of Python iterators and generators
- Basic SQL knowledge
- Familiarity with AST (Abstract Syntax Trees)

### Setup Development Environment

```bash
# Clone or navigate to the project
cd sql_engine

# Install in editable mode
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest
```

## Codebase Overview

### Architecture Layers

```
┌─────────────────────────────────────┐
│         Public API (engine.py)      │
│  - Engine class                     │
│  - register() / query() methods     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Query Processing Pipeline      │
│  ┌──────────┐  ┌──────────┐        │
│  │ Parser   │→ │ Planner  │        │
│  └──────────┘  └────┬─────┘        │
│                     │               │
│              ┌─────▼─────┐         │
│              │ Executor  │         │
│              └─────┬─────┘         │
└────────────────────┼────────────────┘
                     │
┌────────────────────▼────────────────┐
│      Iterator Operators              │
│  Scan → Filter → Join → Project     │
└─────────────────────────────────────┘
```

## Core Components Deep Dive

### 1. Engine (`engine.py`)

**File**: `streaming_sql_engine/engine.py`

**Purpose**: Main entry point for users

**Key Methods**:

```python
def register(self, table_name, source_fn, ordered_by=None):
    """
    Register a table source.

    Args:
        table_name: Name used in SQL queries
        source_fn: Function returning Iterator[Dict[str, Any]]
        ordered_by: Column name if source is sorted (for merge joins)
    """
```

**Design Notes**:

- Stores sources as callable functions (lazy evaluation)
- Metadata stored separately for join optimization
- No validation of source functions until query time

**Testing**:

```python
def test_engine_register():
    engine = Engine()
    engine.register("users", lambda: iter([{"id": 1}]))
    assert "users" in engine._sources
```

---

### 2. Parser (`parser.py`)

**File**: `streaming_sql_engine/parser.py`

**Purpose**: Convert SQL string to AST

**Dependencies**: `sqlglot` library

**Key Function**:

```python
def parse_sql(sql: str, dialect: Optional[str] = None) -> exp.Select:
    """
    Parse SQL with auto-detection of dialect.

    Tries: mysql → postgres → sqlite
    """
```

**Important Details**:

- sqlglot uses `from_` (underscore) to avoid Python keyword
- Returns `exp.Select` AST node
- Validates unsupported features early

**Extending**:
To support new SQL features, modify `_validate_query()`:

```python
def _validate_query(select: exp.Select) -> None:
    # Add new checks here
    if select.args.get("new_feature"):
        raise ParseError("New feature not yet supported")
```

---

### 3. Planner (`planner.py`)

**File**: `streaming_sql_engine/planner.py`

**Purpose**: Extract query structure from AST

**Key Functions**:

#### `build_logical_plan()`

Converts AST to `LogicalPlan`:

```python
def build_logical_plan(ast, registered_tables):
    # Extract FROM
    from_expr = ast.args.get("from_")
    root_table, root_alias = _extract_table_and_alias(from_expr.this)

    # Extract JOINs
    joins = []
    for join_expr in ast.args.get("joins", []):
        joins.append(_extract_join(join_expr, registered_tables))

    # Extract WHERE
    where_expr = ast.args.get("where")

    # Extract SELECT
    projections = list(ast.expressions)

    return LogicalPlan(...)
```

#### `_extract_join()`

Extracts join information:

- Join type (INNER/LEFT)
- Table and alias
- Join keys from ON clause

**Join Key Extraction**:

```python
def _extract_join_keys(on_expr):
    # Only supports: alias1.col1 = alias2.col2
    if not isinstance(on_expr, exp.EQ):
        raise ParseError("Only equality joins")

    left_key = _column_to_string(on_expr.this)
    right_key = _column_to_string(on_expr.expression)
    return left_key, right_key
```

**Extending**:
To support non-equality joins:

1. Modify `_extract_join_keys()` to handle other operators
2. Update `JoinInfo` to store join operator
3. Modify join iterators to handle non-equality

---

### 4. Executor (`executor.py`)

**File**: `streaming_sql_engine/executor.py`

**Purpose**: Build iterator pipeline from logical plan

**Pipeline Construction**:

```python
def execute_plan(plan, sources, source_metadata):
    # 1. Start with scan
    iterator = ScanIterator(sources[plan.root_table], ...)

    # 2. Add filter if WHERE exists
    if plan.where_expr:
        iterator = FilterIterator(iterator, plan.where_expr)

    # 3. Add joins in order
    for join_info in plan.joins:
        iterator = _build_join_iterator(iterator, join_info, ...)

    # 4. Add projection
    iterator = ProjectIterator(iterator, plan.projections)

    return iterator
```

**Join Strategy Selection**:

```python
def _build_join_iterator(...):
    # Check if right side is sorted
    right_ordered_by = source_metadata.get("ordered_by")

    if can_use_merge_join(right_ordered_by, join_key):
        return MergeJoinIterator(...)
    else:
        return LookupJoinIterator(...)
```

**Extending**:
To add new join types:

1. Create new iterator class
2. Add selection logic in `_build_join_iterator()`
3. Handle join semantics

---

### 5. Operators (`operators.py`)

**File**: `streaming_sql_engine/operators.py`

**Purpose**: Iterator implementations for query execution

#### ScanIterator

**Purpose**: Read rows from source function

**Implementation**:

```python
class ScanIterator:
    def __init__(self, source_fn, table_name, alias):
        self.source_fn = source_fn
        self.alias = alias or table_name
        self._iterator = None

    def __next__(self):
        if self._iterator is None:
            self._iterator = iter(self.source_fn())

        row = next(self._iterator)

        # Prefix columns with table alias
        return {f"{self.alias}.{k}": v for k, v in row.items()}
```

**Key Design**:

- Lazy initialization of iterator
- Prefixes columns to avoid conflicts
- Simple pass-through

#### FilterIterator

**Purpose**: Filter rows based on WHERE expression

**Implementation**:

```python
class FilterIterator:
    def __init__(self, source, where_expr):
        self.source = source
        self.where_expr = where_expr

    def __next__(self):
        while True:
            row = next(self.source)
            if evaluate_expression(self.where_expr, row):
                return row
            # Otherwise, continue loop (skip row)
```

**Key Design**:

- Uses `while True` to skip non-matching rows
- Calls `evaluate_expression()` for each row
- Simple but effective

#### LookupJoinIterator

**Purpose**: Hash-based join

**Build Phase** (in `__init__`):

```python
def _build_index(self):
    # Load entire right table
    for row in self.right_source_fn():
        key_value = row[join_key_column]
        if key_value not in self.lookup_index:
            self.lookup_index[key_value] = []
        self.lookup_index[key_value].append(row)
```

**Probe Phase** (in `__next__`):

```python
def __next__(self):
    left_row = next(self.left_source)
    left_key = self._get_key_value(left_row, self.left_key)

    # Lookup
    matches = self.lookup_index.get(left_key, [])

    # Handle INNER vs LEFT JOIN
    if self.join_type == "INNER" and not matches:
        return self.__next__()  # Skip, try next

    if self.join_type == "LEFT" and not matches:
        return left_row  # Return with NULLs

    # Yield match
    return {**left_row, **matches[self._match_index]}
```

**Key Design**:

- Builds index once in `__init__`
- Handles duplicate keys (list of rows)
- Tracks match index for multiple matches per key

#### MergeJoinIterator

**Purpose**: Merge join for sorted data

**Algorithm**:

```python
def __next__(self):
    # Get left row
    left_row = next(self.left_source)
    left_key = get_key(left_row)

    # Advance right until match
    while right_key < left_key:
        advance_right()

    if right_key == left_key:
        # Collect all rows with same key
        fill_right_buffer(left_key)
        return combine(left_row, right_buffer[current])
    elif right_key > left_key:
        # No match
        if LEFT JOIN:
            return left_row  # with NULLs
        else:
            return self.__next__()  # Skip
```

**Key Design**:

- Single pass through both tables
- Buffers equal-key runs
- Very memory efficient

#### ProjectIterator

**Purpose**: Apply SELECT projection

**Implementation**:

```python
class ProjectIterator:
    def __next__(self):
        row = next(self.source)
        result = {}

        for expr in self.projections:
            if isinstance(expr, exp.Alias):
                # SELECT col AS alias
                alias = expr.alias
                value = evaluate_expression(expr.this, row)
                result[alias] = value
            elif isinstance(expr, exp.Column):
                # SELECT alias.col
                col_name = f"{expr.table}.{expr.name}"
                result[expr.name] = row[col_name]

        return result
```

**Key Design**:

- Handles aliases (`AS`)
- Handles column references
- Evaluates expressions if needed

---

### 6. Evaluator (`evaluator.py`)

**File**: `streaming_sql_engine/evaluator.py`

**Purpose**: Evaluate SQL expressions against row data

**Recursive Evaluation**:

```python
def evaluate_expression(expr, row):
    # Base cases
    if isinstance(expr, exp.Column):
        return row[f"{expr.table}.{expr.name}"]

    if isinstance(expr, exp.Literal):
        return expr.this

    # Recursive cases
    if isinstance(expr, exp.EQ):
        left = evaluate_expression(expr.this, row)
        right = evaluate_expression(expr.expression, row)
        return left == right

    # ... more expression types
```

**Key Design**:

- Recursive tree traversal
- Bottom-up evaluation
- Short-circuit for AND/OR

**Extending**:
To add new expression types:

```python
elif isinstance(expr, exp.NewExpression):
    # Evaluate recursively
    left = evaluate_expression(expr.this, row)
    right = evaluate_expression(expr.expression, row)
    return left <operator> right
```

---

### 7. Database Connector (`db_connector.py`)

**File**: `streaming_sql_engine/db_connector.py`

**Purpose**: Database connection utilities

**Key Classes**:

#### PostgreSQLPool

- Uses `psycopg2.pool.ThreadedConnectionPool`
- Context manager for connections
- Server-side cursors for streaming

#### MySQLPool

- Uses `dbutils.pooled_db.PooledDB` with `pymysql`
- DictCursor for dictionary rows
- Connection pooling

**Streaming Query**:

```python
def stream_query(pool, query, params=None, fetch_size=1000):
    with pool.get_connection() as conn:
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute(query, params)

        while True:
            rows = cursor.fetchmany(fetch_size)
            if not rows:
                break
            for row in rows:
                yield dict(row)
```

**Key Design**:

- Uses `fetchmany()` for batching
- Yields rows one at a time
- Handles both PostgreSQL and MySQL

---

## Common Patterns

### Adding a New Operator

1. **Create the class**:

```python
class NewOperator:
    def __init__(self, source, param):
        self.source = source
        self.param = param

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self.source)
        # Transform row
        return transformed_row
```

2. **Add to executor**:

```python
# In executor.py
if needs_new_operator:
    iterator = NewOperator(iterator, param)
```

### Adding Expression Support

1. **Add to evaluator**:

```python
# In evaluator.py
elif isinstance(expr, exp.NewExpression):
    left = evaluate_expression(expr.this, row)
    right = evaluate_expression(expr.expression, row)
    return left <operation> right
```

2. **Update parser validation** (if needed):

```python
# In parser.py
def _validate_query(select):
    # Check if new expression is allowed
    pass
```

### Debugging Tips

1. **Add logging**:

```python
import logging
logger = logging.getLogger(__name__)

def __next__(self):
    row = next(self.source)
    logger.debug(f"Processing row: {row}")
    return row
```

2. **Print AST**:

```python
from sqlglot import parse_one
ast = parse_one("SELECT * FROM users")
print(ast.sql())  # Pretty print
print(ast.args)   # See structure
```

3. **Inspect iterator state**:

```python
# Add breakpoints in __next__ methods
# Check self._left_row, self._right_buffer, etc.
```

---

## Testing

### Unit Testing Operators

```python
def test_filter_iterator():
    source = iter([
        {"id": 1, "active": 1},
        {"id": 2, "active": 0},
        {"id": 3, "active": 1}
    ])

    # Create WHERE expression: active = 1
    where_expr = exp.EQ(
        this=exp.Column(name="active"),
        expression=exp.Literal(this=1)
    )

    iterator = FilterIterator(source, where_expr)
    results = list(iterator)

    assert len(results) == 2
    assert results[0]["id"] == 1
    assert results[1]["id"] == 3
```

### Integration Testing

```python
def test_full_query():
    engine = Engine()
    engine.register("users", lambda: iter([{"id": 1, "name": "Alice"}]))
    engine.register("depts", lambda: iter([{"id": 10, "name": "Eng"}]))

    query = """
        SELECT users.name, depts.name
        FROM users
        JOIN depts ON users.dept_id = depts.id
    """

    results = list(engine.query(query))
    assert len(results) == 1
    assert results[0]["name"] == "Alice"
```

---

## Performance Profiling

### Profile Memory Usage

```python
import tracemalloc

tracemalloc.start()
# Run query
results = list(engine.query(query))
current, peak = tracemalloc.get_traced_memory()
print(f"Peak memory: {peak / 1024 / 1024} MB")
```

### Profile Execution Time

```python
import time

start = time.time()
results = list(engine.query(query))
elapsed = time.time() - start
print(f"Query took {elapsed:.2f} seconds")
```

### Profile with cProfile

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
results = list(engine.query(query))
profiler.disable()
profiler.print_stats()
```

---

## Code Style

### Follow PEP 8

- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions

### Type Hints

```python
from typing import Iterator, Dict, Any, Optional

def process_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single row."""
    return row
```

### Error Handling

```python
try:
    result = risky_operation()
except SpecificError as e:
    raise ParseError(f"Failed to parse: {e}") from e
```

---

## Contributing

### Before Submitting

1. Run linter: `flake8 streaming_sql_engine/`
2. Run formatter: `black streaming_sql_engine/`
3. Write tests for new features
4. Update documentation

### Pull Request Checklist

- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No performance regressions
- [ ] Handles edge cases

---

## Resources

### External Libraries

- **sqlglot**: SQL parsing and AST manipulation

  - Docs: https://github.com/tobymao/sqlglot
  - Used for: Parsing SQL, AST traversal

- **psycopg2**: PostgreSQL adapter

  - Docs: https://www.psycopg.org/docs/
  - Used for: PostgreSQL connections

- **pymysql**: MySQL adapter
  - Docs: https://github.com/PyMySQL/PyMySQL
  - Used for: MySQL connections

### Internal Documentation

- `TECHNICAL_DOCUMENTATION.md`: Architecture and design
- `README.md`: User documentation
- `PERFORMANCE.md`: Performance characteristics

---

## Questions?

For questions about the codebase:

1. Check `TECHNICAL_DOCUMENTATION.md` for architecture
2. Read code comments
3. Review test files for usage examples
4. Check GitHub issues (if applicable)
