"""
Execution engine - builds iterator pipeline from logical plan.
"""

from .planner import LogicalPlan, JoinInfo
from .operators import (
    ScanIterator,
    FilterIterator,
    ProjectIterator,
    LookupJoinIterator,
    MergeJoinIterator
)

# Try importing Polars operators (optional)
try:
    from .operators_polars import (
        PolarsLookupJoinIterator,
        PolarsBatchFilterIterator,
        PolarsBatchProjectIterator,
        should_use_polars
    )
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    PolarsBatchFilterIterator = None
    PolarsBatchProjectIterator = None

# Try importing mmap operators (optional)
try:
    from .operators_mmap import MmapLookupJoinIterator
    MMAP_AVAILABLE = True
except ImportError:
    MMAP_AVAILABLE = False
    MmapLookupJoinIterator = None


def execute_plan(
    plan,
    sources,
    source_metadata,
    debug=False,
    use_polars=True,
    first_match_only=False
):
    """
    Execute a logical plan and return a generator of result row dictionaries.
    
    Args:
        plan: Logical execution plan (with optimizations: required_columns, pushable_where_expr)
        sources: Dictionary mapping table names to source functions
        source_metadata: Dictionary with metadata about sources (e.g., ordered_by)
        
    Returns:
        Generator of result row dictionaries
    """
    # Get required columns for root table (column pruning)
    root_required_columns = plan.required_columns.get(plan.root_table)
    
    # Handle pushable WHERE clause (filter pushdown)
    # For sources that support the protocol, we can push WHERE to the source
    # For other sources, we'll apply it after scanning
    root_source_fn = sources[plan.root_table]
    pushable_where_sql = None
    
    if plan.pushable_where_expr:
        # Convert pushable WHERE expression to SQL string
        from .optimizer import expression_to_sql_string
        try:
            pushable_where_sql = expression_to_sql_string(plan.pushable_where_expr)
            if debug:
                print(f"  [OPTIMIZATION] Pushing WHERE clause to source: {pushable_where_sql}")
        except Exception as e:
            if debug:
                print(f"  [OPTIMIZATION] Could not push WHERE clause: {e}")
            pushable_where_sql = None
    
    # Check if source supports optimization via protocol
    # Protocol: If function accepts dynamic_where or dynamic_columns parameters, optimizations apply
    import inspect
    
    def source_supports_optimizations(source_fn):
        """Check if source implements optimization protocol."""
        try:
            sig = inspect.signature(source_fn)
            params = list(sig.parameters.keys())
            return 'dynamic_where' in params or 'dynamic_columns' in params
        except (ValueError, TypeError):
            # Can't inspect signature, assume no protocol
            return False
    
    # Apply optimizations if protocol is supported
    if source_supports_optimizations(root_source_fn) and (root_required_columns or pushable_where_sql):
        if debug:
            print(f"  [OPTIMIZATION] Source supports protocol - applying column pruning and filter pushdown")
        
        original_source_fn = root_source_fn
        
        def optimized_source_fn():
            # Call source with optimization parameters
            return original_source_fn(
                dynamic_where=pushable_where_sql,
                dynamic_columns=list(root_required_columns) if root_required_columns else None
            )
        
        root_source_fn = optimized_source_fn
    
    # Start with scan of root table
    if debug:
        if root_required_columns:
            print(f"  [SCAN] Scanning table: {plan.root_table} (columns: {len(root_required_columns)})")
        else:
            print(f"  [SCAN] Scanning table: {plan.root_table}")
    
    iterator = ScanIterator(
        root_source_fn,
        plan.root_table,
        plan.root_alias,
        required_columns=root_required_columns,
        debug=debug
    )
    
    # Apply joins in order
    # Track WHERE clauses that have been pushed to sources
    remaining_where_expr = plan.where_expr
    if debug and remaining_where_expr:
        print(f"  [DEBUG] Initial remaining_where_expr: {remaining_where_expr}")
    
    for i, join_info in enumerate(plan.joins, 1):
        # Get required columns for joined table (needed for optimizations)
        join_required_columns = plan.required_columns.get(join_info.table)
        
        if debug:
            if join_required_columns:
                print(f"  [JOIN {i}/{len(plan.joins)}] {join_info.join_type} JOIN {join_info.table} (columns: {len(join_required_columns)})")
            else:
                print(f"  [JOIN {i}/{len(plan.joins)}] {join_info.join_type} JOIN {join_info.table}")
        
        # Check if we can push WHERE clauses to this joined table
        right_source_fn = sources[join_info.table]
        join_where_sql = None
        table_where_expr = None
        
        # Extract WHERE clauses that reference this joined table
        if remaining_where_expr:
            from .optimizer import extract_table_where_clauses, expression_to_sql_string, remove_expression_from_where
            if debug:
                print(f"  [DEBUG] remaining_where_expr is not None: {remaining_where_expr}")
            try:
                # Try both alias and table name (WHERE clause might use either)
                table_alias = join_info.alias or join_info.table
                table_name = join_info.table
                
                if debug:
                    print(f"  [DEBUG] Checking WHERE clauses for alias '{table_alias}' or table '{table_name}'")
                    print(f"  [DEBUG] Remaining WHERE expr: {remaining_where_expr}")
                
                # Try alias first, then table name
                table_where_expr = extract_table_where_clauses(remaining_where_expr, table_alias)
                if not table_where_expr and table_alias != table_name:
                    # If alias didn't match and it's different from table name, try table name
                    table_where_expr = extract_table_where_clauses(remaining_where_expr, table_name)
                
                if table_where_expr:
                    join_where_sql = expression_to_sql_string(table_where_expr)
                    if debug:
                        print(f"  [OPTIMIZATION] Pushing WHERE clause to {join_info.table}: {join_where_sql}")
                    # Remove pushed clauses from remaining WHERE
                    remaining_where_expr = remove_expression_from_where(remaining_where_expr, table_where_expr)
                    if debug:
                        print(f"  [DEBUG] Remaining WHERE after removal: {remaining_where_expr}")
                else:
                    if debug:
                        print(f"  [DEBUG] No WHERE clauses found for alias '{table_alias}' or table '{table_name}'")
            except Exception as e:
                if debug:
                    print(f"  [OPTIMIZATION] Could not push WHERE to {join_info.table}: {e}")
                    import traceback
                    traceback.print_exc()
                else:
                    # Even if not debug, log the error so we can see what's wrong
                    import traceback
                    print(f"  [ERROR] Could not push WHERE to {join_info.table}: {e}")
                    traceback.print_exc()
                join_where_sql = None
        
        # Apply protocol optimizations to joined table source if supported
        import inspect
        def source_supports_optimizations(source_fn):
            """Check if source implements optimization protocol."""
            try:
                sig = inspect.signature(source_fn)
                params = list(sig.parameters.keys())
                return 'dynamic_where' in params or 'dynamic_columns' in params
            except (ValueError, TypeError):
                return False
        
        optimized_right_source_fn = right_source_fn
        if source_supports_optimizations(right_source_fn) and (join_required_columns or join_where_sql):
            if debug:
                print(f"  [OPTIMIZATION] Source {join_info.table} supports protocol - applying optimizations")
            
            original_right_source_fn = right_source_fn
            
            def optimized_right_source_fn():
                # Call source with optimization parameters
                return original_right_source_fn(
                    dynamic_where=join_where_sql,
                    dynamic_columns=list(join_required_columns) if join_required_columns else None
                )
        
        iterator = _build_join_iterator(
            iterator,
            join_info,
            sources,
            source_metadata,
            plan.required_columns.get(join_info.table),  # Pass required columns
            optimized_right_source_fn=optimized_right_source_fn,  # Pass optimized source
            debug=debug,
            use_polars=use_polars,  # Pass Polars flag
            first_match_only=first_match_only  # Pass first-match-only flag
        )
    
    # Update plan.where_expr to only include clauses not pushed to sources
    plan.where_expr = remaining_where_expr
    
    # Apply WHERE filter if present (non-pushable conditions)
    # Must be applied AFTER joins since remaining WHERE conditions may reference joined tables
    if plan.where_expr:
        if debug:
            print(f"  [FILTER] Applying WHERE clause (non-pushable conditions)")
        
        # Use Polars batch filtering if available and beneficial
        if (use_polars and POLARS_AVAILABLE and PolarsBatchFilterIterator is not None):
            if debug:
                print(f"  [POLARS] Using Polars vectorized filtering (SIMD-accelerated)")
            try:
                iterator = PolarsBatchFilterIterator(iterator, plan.where_expr, batch_size=10000, debug=debug)
            except Exception as e:
                if debug:
                    print(f"  [POLARS] ✗ Filtering failed: {e}, using Python")
                iterator = FilterIterator(iterator, plan.where_expr, debug=debug)
        else:
            iterator = FilterIterator(iterator, plan.where_expr, debug=debug)
    
    # Apply projection
    if debug:
        print(f"  [PROJECT] Applying SELECT projection")
        print(f"\nPipeline ready. Starting row processing...\n")
        print("-" * 60)
    
    # Use Polars batch projection if available and beneficial
    if (use_polars and POLARS_AVAILABLE and PolarsBatchProjectIterator is not None):
        if debug:
            print(f"  [POLARS] Using Polars vectorized projection (SIMD-accelerated)")
        try:
            iterator = PolarsBatchProjectIterator(iterator, plan.projections, batch_size=10000, debug=debug)
        except Exception as e:
            if debug:
                print(f"  [POLARS] ✗ Projection failed: {e}, using Python")
            iterator = ProjectIterator(iterator, plan.projections, debug=debug)
    else:
        iterator = ProjectIterator(iterator, plan.projections, debug=debug)
    
    return iterator
    
    
def _build_join_iterator(
    left_iterator,
    join_info,
    sources,
    source_metadata,
    required_columns=None,
    optimized_right_source_fn=None,
    debug=False,
    use_polars=True,
    first_match_only=False
):
    """
    Build appropriate join iterator based on source capabilities.
    
    Args:
        required_columns: Set of column names needed from right table (for column pruning)
        optimized_right_source_fn: Optional optimized source function (with protocol applied)
    """
    # Use optimized source if provided, otherwise use original
    if optimized_right_source_fn is not None:
        right_source = optimized_right_source_fn
    else:
        right_source = sources[join_info.table]
    right_metadata = source_metadata.get(join_info.table, {})
    
    # Apply column pruning to right source if needed
    # For database sources, this would be handled at source creation
    # For other sources, LookupJoinIterator will handle it via ScanIterator
    
    # Check if both sides are ordered by join keys
    # Extract left table name to check its metadata
    left_table_name = _extract_table_from_key(join_info.left_key)
    left_metadata = source_metadata.get(left_table_name, {}) if left_table_name else {}
    left_ordered_by = left_metadata.get("ordered_by")
    right_ordered_by = right_metadata.get("ordered_by")
    
    # Extract column names from join keys
    left_join_column = _extract_column_from_key(join_info.left_key)
    right_join_column = _extract_column_from_key(join_info.right_key)
    
    # For merge join, we need BOTH sides sorted on their respective join keys
    # Merge join REQUIRES sorted data - if data isn't sorted, it produces incorrect results
    # Only use merge join when:
    # 1. Explicitly told both sides are sorted (via ordered_by metadata)
    # 2. NOT using Polars (Polars is faster for unsorted data, merge join only for sorted)
    use_merge_join = (
        not use_polars and  # Don't use merge join if Polars is explicitly requested
        left_ordered_by is not None and
        left_ordered_by == left_join_column and
        right_ordered_by is not None and
        right_ordered_by == right_join_column
    )
    
    if use_merge_join:
        if debug:
            iterator_type = "MERGE JOIN"
            print(f"      Using {iterator_type} (sorted data)")
            print(f"      Left ordered_by: {left_ordered_by}, Right ordered_by: {right_ordered_by}")
            print(f"      Left join column: {left_join_column}, Right join column: {right_join_column}")
        return MergeJoinIterator(
            left_iterator,
            right_source,
            join_info.left_key,
            join_info.right_key,
            join_info.join_type,
            join_info.table,
            join_info.alias,
            debug=debug
        )
    else:
        # When use_polars=True is explicitly set, prioritize Polars over mmap
        # (unless user explicitly wants mmap by providing filename)
        right_metadata = source_metadata.get(join_info.table, {})
        right_table_filename = right_metadata.get("filename")
        
        # Only use mmap if:
        # 1. Filename is explicitly provided (user wants mmap)
        # 2. Polars is NOT explicitly requested (use_polars=False)
        # This ensures that when user sets use_polars=True, Polars is used instead of mmap
        use_mmap = (
            MMAP_AVAILABLE and 
            MmapLookupJoinIterator is not None and 
            right_table_filename and
            not use_polars  # Don't use mmap if Polars is explicitly requested
        )
        
        if use_mmap:
            if debug:
                iterator_type = "MMAP LOOKUP JOIN"
                if required_columns:
                    print(f"      Using {iterator_type} (low memory, columns: {len(required_columns)})...")
                else:
                    print(f"      Using {iterator_type} (low memory, position-based index)...")
            try:
                return MmapLookupJoinIterator(
                    left_iterator,
                    right_source,
                    join_info.left_key,
                    join_info.right_key,
                    join_info.join_type,
                    join_info.table,
                    join_info.alias,
                    right_table_filename=right_table_filename,
                    required_columns=required_columns,
                    debug=debug
                )
            except Exception as e:
                if debug:
                    print(f"      ⚠️  Mmap join failed: {e}")
                    import traceback
                    traceback.print_exc()
                    print(f"      Falling back to Polars/Python")
                # Fallback to Polars or Python
                pass
        
        # Decide between Polars and Python implementation
        # When use_polars=True, Polars is prioritized (unless mmap explicitly requested via filename)
        if debug:
            if use_polars:
                if POLARS_AVAILABLE:
                    print(f"      [POLARS] Checking if Polars should be used...")
                    try:
                        should_use = should_use_polars(right_source, threshold=10000)
                        if not should_use:
                            print(f"      [POLARS] Right side too small or estimation failed, using Python join instead")
                    except Exception as e:
                        print(f"      [POLARS] Estimation failed: {e}, using Python join instead")
                else:
                    print(f"      [POLARS] Polars not available (not installed), falling back to Python")
        
        if (use_polars and POLARS_AVAILABLE and 
            should_use_polars(right_source, threshold=10000)):
            if debug:
                iterator_type = "POLARS LOOKUP JOIN"
                print(f"      [POLARS] ✓ Using {iterator_type} (SIMD-accelerated)")
                if required_columns:
                    print(f"      [POLARS]   Columns: {len(required_columns)}")
                if first_match_only:
                    print(f"      [POLARS]   ⚡ First-match-only mode enabled")
            try:
                return PolarsLookupJoinIterator(
                    left_iterator,
                    right_source,
                    join_info.left_key,
                    join_info.right_key,
                    join_info.join_type,
                    join_info.table,
                    join_info.alias,
                    batch_size=10000,
                    required_columns=required_columns,
                    debug=debug,
                    first_match_only=first_match_only
                )
            except Exception as e:
                if debug:
                    print(f"      [POLARS] ✗ Polars join failed: {e}, falling back to Python")
                # Fallback to Python implementation
                pass
        
        if debug:
            iterator_type = "LOOKUP JOIN (Python)"
            if required_columns:
                print(f"      Using {iterator_type} (building index, columns: {len(required_columns)})...")
            else:
                print(f"      Using {iterator_type} (building index...)")
            if first_match_only:
                print(f"      ⚡ First-match-only mode enabled")
        return LookupJoinIterator(
            left_iterator,
            right_source,
            join_info.left_key,
            join_info.right_key,
            join_info.join_type,
            join_info.table,
            join_info.alias,
            required_columns=required_columns,
            debug=debug,
            first_match_only=first_match_only
        )


def _extract_table_from_key(key):
    """Extract table alias from a key like 'alias.column'."""
    if "." in key:
        return key.split(".", 1)[0]
    return None


def _extract_column_from_key(key):
    """Extract column name from a key like 'alias.column'."""
    if "." in key:
        return key.split(".", 1)[1]
    return key

