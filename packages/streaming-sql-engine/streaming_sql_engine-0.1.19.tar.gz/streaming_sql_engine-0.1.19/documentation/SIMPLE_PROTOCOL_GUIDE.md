# Simple Protocol Guide - Automated Protocol Support

## The Problem

Implementing protocol support manually is complicated:

- Need to parse SQL WHERE clauses
- Need to use evaluator
- Need to handle column pruning
- Lots of boilerplate code

## The Solution: Helper Functions

We've created helper functions that **automate everything**!

---

## Method 1: Register File Sources (Easiest!)

**Before (complicated):**

```python
def jsonl_source(filepath, dynamic_where=None, dynamic_columns=None):
    # Parse WHERE clause
    # Use evaluator
    # Handle column pruning
    # ... 50+ lines of code ...
```

**After (simple):**

```python
from streaming_sql_engine.protocol_helpers import register_file_source

register_file_source(engine, "products", "data/products.jsonl")
register_file_source(engine, "categories", "data/categories.csv")

# That's it! Protocol support is automatic
```

---

## Method 2: Use Decorator (For Custom Sources)

**Before:**

```python
def my_source(filepath):
    # Your code
    for row in read_file(filepath):
        yield row

# Need to manually add protocol support...
```

**After:**

```python
from streaming_sql_engine.protocol_helpers import add_protocol_support

@add_protocol_support
def my_source(filepath):
    # Your code
    for row in read_file(filepath):
        yield row

# Protocol support added automatically!
```

---

## Method 3: Wrap Existing Function

**Before:**

```python
def existing_source(filepath):
    # Your existing code (no protocol)
    ...

# Need to rewrite to add protocol...
```

**After:**

```python
from streaming_sql_engine.protocol_helpers import wrap_simple_source

# Wrap it
protocol_source = wrap_simple_source(existing_source)

# Now it has protocol support!
```

---

## Method 4: Register API Sources

**Before:**

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    # Parse WHERE clause
    # Convert to query parameters
    # Handle pagination
    # ... 100+ lines of code ...
```

**After:**

```python
from streaming_sql_engine.protocol_helpers import register_api_source

register_api_source(
    engine,
    "customers",
    "http://localhost:8000",
    "customers"
)

# That's it! Protocol support is automatic
```

---

## Complete Example

```python
from streaming_sql_engine import Engine
from streaming_sql_engine.protocol_helpers import (
    register_file_source,
    register_api_source,
)

# Create engine
engine = Engine(debug=True)

# Register file sources (automatic protocol!)
register_file_source(engine, "products", "data/products.jsonl")
register_file_source(engine, "categories", "data/categories.csv")

# Register API source (automatic protocol!)
register_api_source(engine, "customers", "http://localhost:8000", "customers")

# Query with automatic optimizations
for row in engine.query("""
    SELECT products.name, categories.name AS category
    FROM products
    JOIN categories ON products.category_id = categories.id
    WHERE products.price > 100
"""):
    print(row)
```

**That's it!** No manual SQL parsing, no manual filtering, no manual column pruning.

---

## Available Helpers

### `register_file_source(engine, table_name, filepath, filename=None, ordered_by=None)`

Register a file source with automatic protocol support.

**Parameters:**

- `engine`: Engine instance
- `table_name`: Table name for SQL queries
- `filepath`: Path to file (JSONL or CSV)
- `filename`: Optional filename for mmap joins
- `ordered_by`: Optional column name for merge joins

**Example:**

```python
register_file_source(engine, "products", "data/products.jsonl")
```

---

### `register_api_source(engine, table_name, api_url, endpoint, where_to_params=None)`

Register an API source with automatic protocol support.

**Parameters:**

- `engine`: Engine instance
- `table_name`: Table name for SQL queries
- `api_url`: Base URL of API
- `endpoint`: API endpoint path
- `where_to_params`: Optional function to convert WHERE clause to query params

**Example:**

```python
register_api_source(engine, "customers", "http://localhost:8000", "customers")
```

---

### `@add_protocol_support`

Decorator that adds protocol support to any source function.

**Example:**

```python
@add_protocol_support
def my_source(filepath: str):
    with open(filepath) as f:
        for line in f:
            yield json.loads(line)
```

---

### `wrap_simple_source(source_fn)`

Wrap an existing source function to add protocol support.

**Example:**

```python
def existing_source(filepath: str):
    # Your existing code
    ...

protocol_source = wrap_simple_source(existing_source)
```

---

### `create_protocol_source(filepath, file_type='auto')`

Create a protocol-enabled source function from a file path.

**Example:**

```python
source = create_protocol_source("data/products.jsonl")
engine.register("products", source)
```

---

## Benefits

✅ **No manual SQL parsing** - Handled automatically  
✅ **No manual filter evaluation** - Uses engine's evaluator  
✅ **No manual column pruning** - Handled automatically  
✅ **Works with any source type** - Files, APIs, databases  
✅ **Same performance** - Uses same optimizations as manual implementation

---

## When to Use What

- **File sources**: Use `register_file_source()` (easiest!)
- **API sources**: Use `register_api_source()` (easiest!)
- **Custom sources**: Use `@add_protocol_support` decorator
- **Existing code**: Use `wrap_simple_source()`
- **Advanced**: Use `create_protocol_source()` for more control

---

## Summary

**Before:** 50-100 lines of manual protocol implementation  
**After:** 1 line with helper functions

**Protocol support is now automatic!** 🎉


