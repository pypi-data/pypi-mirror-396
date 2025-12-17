"""
Protocol Helpers - Automate Protocol Implementation

These helpers make it easy to add protocol support to any source function
without manual SQL parsing or evaluation.
"""

from typing import Iterator, Dict, Optional, Callable
from functools import wraps


def add_protocol_support(source_fn: Callable) -> Callable:
    """
    Decorator that automatically adds protocol support to any source function.
    
    Usage:
        @add_protocol_support
        def my_source(filepath: str) -> Iterator[Dict]:
            with open(filepath) as f:
                for line in f:
                    yield json.loads(line)
        
        # Now it automatically supports dynamic_where and dynamic_columns!
        engine.register("products", lambda dynamic_where=None, dynamic_columns=None: 
                       my_source("data.jsonl", dynamic_where, dynamic_columns))
    
    The decorator handles:
    - Parsing WHERE clause using sqlglot
    - Evaluating filters using engine's evaluator
    - Column pruning
    """
    @wraps(source_fn)
    def wrapper(*args, dynamic_where: Optional[str] = None, 
                dynamic_columns: Optional[list] = None, **kwargs):
        # Get iterator from original source
        iterator = source_fn(*args, **kwargs)
        
        # Apply filter pushdown if WHERE clause provided
        if dynamic_where:
            iterator = _apply_filter(iterator, dynamic_where)
        
        # Apply column pruning if columns specified
        if dynamic_columns:
            iterator = _apply_column_pruning(iterator, dynamic_columns)
        
        return iterator
    
    return wrapper


def _apply_filter(iterator: Iterator[Dict], where_clause: str) -> Iterator[Dict]:
    """Apply WHERE clause filter to iterator using engine's evaluator."""
    # Parse WHERE clause
    try:
        from sqlglot import parse_one
        parsed = parse_one(f"SELECT * FROM dummy WHERE {where_clause}")
        where_expr = parsed.args.get('where')
        if where_expr:
            where_expr = where_expr.this
        else:
            return iterator
    except Exception:
        # If parsing fails, return iterator unchanged
        return iterator
    
    # Apply filter using evaluator
    try:
        from streaming_sql_engine.evaluator import evaluate_expression
        
        for row in iterator:
            # Prepare row for evaluation (remove table prefix)
            eval_row = {k.split('.')[-1]: v for k, v in row.items()}
            eval_row.update(row)  # Keep original keys too
            
            try:
                if evaluate_expression(where_expr, eval_row):
                    yield row
            except Exception:
                # If evaluation fails, skip row (conservative)
                continue
    except ImportError:
        # If evaluator not available, return iterator unchanged
        return iterator


def _apply_column_pruning(iterator: Iterator[Dict], columns: list) -> Iterator[Dict]:
    """Apply column pruning to iterator."""
    for row in iterator:
        yield {k: v for k, v in row.items() if k in columns}


def wrap_simple_source(source_fn: Callable) -> Callable:
    """
    Wrap a simple source function to add protocol support.
    
    Usage:
        def my_csv_source(filepath: str) -> Iterator[Dict]:
            with open(filepath) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
        
        # Wrap it
        protocol_source = wrap_simple_source(my_csv_source)
        
        # Register with protocol support
        engine.register("products", 
                       lambda dynamic_where=None, dynamic_columns=None:
                       protocol_source("data.csv", dynamic_where, dynamic_columns))
    """
    @wraps(source_fn)
    def protocol_wrapper(*args, dynamic_where: Optional[str] = None,
                        dynamic_columns: Optional[list] = None, **kwargs):
        iterator = source_fn(*args, **kwargs)
        
        if dynamic_where:
            iterator = _apply_filter(iterator, dynamic_where)
        
        if dynamic_columns:
            iterator = _apply_column_pruning(iterator, dynamic_columns)
        
        return iterator
    
    return protocol_wrapper


def create_protocol_source(filepath: str, file_type: str = 'auto') -> Callable:
    """
    Create a protocol-enabled source function from a file path.
    
    Usage:
        # Auto-detect file type
        source = create_protocol_source("data/products.jsonl")
        engine.register("products", source)
        
        # Specify file type
        source = create_protocol_source("data/products.csv", file_type='csv')
        engine.register("products", source)
    
    Supported file types: 'jsonl', 'csv', 'auto' (detects from extension)
    """
    import os
    
    # Auto-detect file type
    if file_type == 'auto':
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.jsonl':
            file_type = 'jsonl'
        elif ext == '.csv':
            file_type = 'csv'
        else:
            raise ValueError(f"Could not auto-detect file type for {filepath}")
    
    def jsonl_source(dynamic_where: Optional[str] = None,
                    dynamic_columns: Optional[list] = None) -> Iterator[Dict]:
        import json
        print(f"  📂 Reading JSONL: {filepath}")
        if dynamic_where:
            print(f"     ✅ Filter pushdown: {dynamic_where}")
        if dynamic_columns:
            print(f"     ✅ Column pruning: {dynamic_columns}")
        
        # Parse WHERE clause ONCE (not for every row!)
        where_expr = None
        if dynamic_where:
            try:
                from sqlglot import parse_one
                parsed = parse_one(f"SELECT * FROM dummy WHERE {dynamic_where}")
                where_expr = parsed.args.get('where')
                if where_expr:
                    where_expr = where_expr.this
            except Exception:
                where_expr = None
        
        # Import evaluator ONCE
        evaluate_expression = None
        if where_expr:
            try:
                from streaming_sql_engine.evaluator import evaluate_expression as eval_fn
                evaluate_expression = eval_fn
            except ImportError:
                evaluate_expression = None
        
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    
                    # Apply filter directly (no iterator creation!)
                    if where_expr and evaluate_expression:
                        # Prepare row for evaluation (remove table prefix)
                        eval_row = {k.split('.')[-1]: v for k, v in row.items()}
                        eval_row.update(row)  # Keep original keys too
                        
                        try:
                            if not evaluate_expression(where_expr, eval_row):
                                continue  # Skip row
                        except Exception:
                            continue  # Skip row on evaluation error
                    
                    # Apply column pruning
                    if dynamic_columns:
                        row = {k: v for k, v in row.items() if k in dynamic_columns}
                    
                    count += 1
                    if count % 1_000_000 == 0:
                        print(f"     Processed {count:,} rows from JSONL...")
                    
                    yield row
                except json.JSONDecodeError:
                    continue
        
        if count > 0:
            print(f"     ✓ Read {count:,} rows from JSONL")
    
    def csv_source(dynamic_where: Optional[str] = None,
                  dynamic_columns: Optional[list] = None) -> Iterator[Dict]:
        import csv
        print(f"  📂 Reading CSV: {filepath}")
        if dynamic_where:
            print(f"     ✅ Filter pushdown: {dynamic_where}")
        if dynamic_columns:
            print(f"     ✅ Column pruning: {dynamic_columns}")
        
        # Parse WHERE clause ONCE (not for every row!)
        where_expr = None
        if dynamic_where:
            try:
                from sqlglot import parse_one
                parsed = parse_one(f"SELECT * FROM dummy WHERE {dynamic_where}")
                where_expr = parsed.args.get('where')
                if where_expr:
                    where_expr = where_expr.this
            except Exception:
                where_expr = None
        
        # Import evaluator ONCE
        evaluate_expression = None
        if where_expr:
            try:
                from streaming_sql_engine.evaluator import evaluate_expression as eval_fn
                evaluate_expression = eval_fn
            except ImportError:
                evaluate_expression = None
        
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Apply filter directly (no iterator creation!)
                if where_expr and evaluate_expression:
                    # Prepare row for evaluation (remove table prefix)
                    eval_row = {k.split('.')[-1]: v for k, v in row.items()}
                    eval_row.update(row)  # Keep original keys too
                    
                    try:
                        if not evaluate_expression(where_expr, eval_row):
                            continue  # Skip row
                    except Exception:
                        continue  # Skip row on evaluation error
                
                # Apply column pruning
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                
                count += 1
                if count % 1_000_000 == 0:
                    print(f"     Processed {count:,} rows from CSV...")
                
                yield row
        
        if count > 0:
            print(f"     ✓ Read {count:,} rows from CSV")
    
    if file_type == 'jsonl':
        return jsonl_source
    elif file_type == 'csv':
        return csv_source
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


# Convenience function for common use case
def register_file_source(engine, table_name: str, filepath: str, 
                        filename: Optional[str] = None, ordered_by: Optional[str] = None):
    """
    Register a file source with automatic protocol support.
    
    Usage:
        register_file_source(engine, "products", "data/products.jsonl")
        register_file_source(engine, "categories", "data/categories.csv")
        
        # With mmap support
        register_file_source(engine, "products", "data/products.jsonl", 
                           filename="data/products.jsonl")
    """
    source_fn = create_protocol_source(filepath)
    engine.register(table_name, source_fn, ordered_by=ordered_by, filename=filename)


def _default_where_to_params(where_clause: str) -> dict:
    """
    Default automatic WHERE-to-params converter.
    Parses SQL WHERE clause and converts to API query parameters.
    
    Handles common patterns automatically:
    - Equality: column = value → params[column] = value
    - Boolean: active = true → params[active] = 'true'
    - Comparisons: price > 100 → params[min_price] = 100
    """
    params = {}
    
    try:
        # Parse SQL WHERE clause using sqlglot
        from sqlglot import parse_one
        parsed = parse_one(f"SELECT * FROM dummy WHERE {where_clause}")
        where_expr = parsed.args.get('where')
        
        if not where_expr:
            return params
        
        where_expr = where_expr.this
        
        # Handle different expression types
        from sqlglot import expressions as exp
        
        def extract_value(expr):
            """Extract literal value from expression."""
            if isinstance(expr, exp.Literal):
                value = expr.this
                # Remove quotes if string
                if isinstance(value, str):
                    return value.strip("'\"")
                return value
            return None
        
        def extract_column(expr):
            """Extract column name from expression."""
            if isinstance(expr, exp.Column):
                return expr.name
            return None
        
        # Handle equality: column = value
        if isinstance(where_expr, exp.EQ):
            col = extract_column(where_expr.this)
            val = extract_value(where_expr.expression)
            if col and val is not None:
                params[col] = str(val)
        
        # Handle AND conditions (multiple filters)
        elif isinstance(where_expr, exp.And):
            # Recursively process both sides
            left_params = _default_where_to_params(str(where_expr.this))
            right_params = _default_where_to_params(str(where_expr.expression))
            params.update(left_params)
            params.update(right_params)
        
        # Handle comparisons: column > value, column < value
        elif isinstance(where_expr, exp.GT):
            col = extract_column(where_expr.this)
            val = extract_value(where_expr.expression)
            if col and val is not None:
                params[f'min_{col}'] = str(val)
        
        elif isinstance(where_expr, exp.LT):
            col = extract_column(where_expr.this)
            val = extract_value(where_expr.expression)
            if col and val is not None:
                params[f'max_{col}'] = str(val)
        
        elif isinstance(where_expr, exp.GTE):
            col = extract_column(where_expr.this)
            val = extract_value(where_expr.expression)
            if col and val is not None:
                params[f'min_{col}'] = str(val)
        
        elif isinstance(where_expr, exp.LTE):
            col = extract_column(where_expr.this)
            val = extract_value(where_expr.expression)
            if col and val is not None:
                params[f'max_{col}'] = str(val)
        
    except Exception:
        # Fallback to simple string matching for common patterns
        where_lower = where_clause.lower()
        
        # Boolean patterns
        if 'active = true' in where_lower or "active = 'true'" in where_lower or "active = 1" in where_lower:
            params['active'] = 'true'
        elif 'active = false' in where_lower or "active = 'false'" in where_lower or "active = 0" in where_lower:
            params['active'] = 'false'
        
        # Country patterns
        if "country = 'us'" in where_lower or "country = \"us\"" in where_lower:
            params['country'] = 'US'
        elif "country = 'uk'" in where_lower or "country = \"uk\"" in where_lower:
            params['country'] = 'UK'
    
    return params


def register_api_source(engine, table_name: str, api_url: str, endpoint: str,
                        where_to_params: Optional[Callable] = None):
    """
    Register an API source with automatic protocol support.
    
    Usage:
        # Simple API source (automatic WHERE-to-params conversion!)
        register_api_source(engine, "customers", "http://localhost:8000", "customers")
        
        # With custom WHERE-to-params converter (only if API has special format)
        def my_converter(where_clause: str) -> dict:
            params = {}
            # Custom conversion logic for your API
            return params
        
        register_api_source(engine, "customers", "http://localhost:8000", "customers",
                           where_to_params=my_converter)
    
    The default converter automatically handles:
    - Equality: column = value → params[column] = value
    - Boolean: active = true → params[active] = 'true'
    - Comparisons: price > 100 → params[min_price] = 100
    - Multiple conditions: AND clauses
    
    Only provide custom converter if your API uses a different format.
    """
    import requests
    
    def api_source(dynamic_where: Optional[str] = None,
                   dynamic_columns: Optional[list] = None) -> Iterator[Dict]:
        print(f"  🌐 Reading from API: {api_url}/{endpoint}")
        if dynamic_where:
            print(f"     ✅ Filter pushdown: {dynamic_where}")
        if dynamic_columns:
            print(f"     ✅ Column pruning: {dynamic_columns}")
        
        params = {}
        
        # Convert WHERE clause to params
        if dynamic_where:
            if where_to_params:
                # Use custom converter
                params.update(where_to_params(dynamic_where))
            else:
                # Use automatic default converter
                params.update(_default_where_to_params(dynamic_where))
        
        # Convert columns to fields param
        if dynamic_columns:
            params['fields'] = ','.join(dynamic_columns)
        
        # Make requests
        page = 1
        page_size = 1000
        total_count = 0
        
        while True:
            params['page'] = page
            params['page_size'] = page_size
            
            try:
                response = requests.get(f"{api_url}/{endpoint}", params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                items = data.get('items', data.get('data', [])) if isinstance(data, dict) else data
                
                if not items:
                    break
                
                for item in items:
                    total_count += 1
                    if total_count % 10_000 == 0:
                        print(f"     Fetched {total_count:,} records from API...")
                    yield item
                
                if isinstance(data, dict) and not data.get('has_more', True):
                    break
                
                page += 1
            except requests.exceptions.RequestException as e:
                print(f"     ⚠️  API error: {e}")
                break
        
        if total_count > 0:
            print(f"     ✓ Fetched {total_count:,} records from API")
    
    engine.register(table_name, api_source)

