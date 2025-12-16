# Architecture Decision: Source Protocol

## What is a "Protocol"?

In Python, a **protocol** is an informal interface. It means: "If your function follows this pattern, the engine will automatically use optimizations."

It's like a contract: **"If you do X, I'll do Y"**

## Current Situation

Right now, the engine uses **TWO** ways to detect optimizations:

1. **Flag-based**: `is_database_source=True` (explicit but redundant)
2. **Protocol-based**: Check function signature (automatic detection)

The code already checks function signatures! So the flag is redundant.

## The Best Approach: Pure Protocol (No Flags)

### Simple Rule: **Everything is an iterator. If your iterator function accepts optimization parameters, optimizations apply automatically.**

---

## Two Types of Sources

### Type 1: Simple Iterator (No Optimizations)

```python
def simple_source():
    """Returns iterator of dicts. No optimizations."""
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

# Register it
engine.register("users", simple_source)
```

**What happens:**
- Engine calls `simple_source()`
- Gets all rows
- Filters/joins happen in Python

---

### Type 2: Optimized Iterator (With Protocol)

```python
def optimized_source(dynamic_where=None, dynamic_columns=None):
    """
    Protocol: Accept these parameters to enable optimizations.
    
    Args:
        dynamic_where: SQL WHERE clause string (e.g., "id > 100")
        dynamic_columns: List of column names (e.g., ["id", "name"])
    
    Returns:
        Iterator of dicts
    """
    # Build query with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM table"
    if where:
        query += f" WHERE {where}"
    
    # Execute and return iterator
    return execute_query(query)

# Register it (NO FLAG NEEDED!)
engine.register("users", optimized_source)
```

**What happens:**
- Engine detects function accepts `dynamic_where` and `dynamic_columns`
- Automatically passes optimizations when available
- Filter pushdown: WHERE clause sent to database
- Column pruning: Only requested columns fetched

---

## How Engine Detects Protocol

The engine uses Python's `inspect.signature()`:

```python
import inspect

def check_if_optimizable(source_fn):
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())
    
    # If function accepts these parameters, it's optimizable
    has_where = 'dynamic_where' in params
    has_columns = 'dynamic_columns' in params
    
    return has_where or has_columns
```

**Automatic detection = No flags needed!**

---

## Examples: Different Source Types

### Example 1: JSONL File (Simple)

```python
def jsonl_source():
    """Simple iterator - no optimizations."""
    with open("data.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", jsonl_source)
```

### Example 2: PostgreSQL (Optimized)

```python
def pg_source(dynamic_where=None, dynamic_columns=None):
    """Optimized - accepts protocol parameters."""
    conn = get_connection()
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM products"
    if where:
        query += f" WHERE {where}"
    
    cursor = conn.execute(query)
    for row in cursor:
        yield dict(row)

engine.register("products", pg_source)  # No flag!
```

### Example 3: REST API (Simple or Optimized)

**Simple version:**
```python
def api_source():
    """Fetch all data, filter in Python."""
    response = requests.get("https://api.example.com/products")
    for item in response.json():
        yield item

engine.register("products", api_source)
```

**Optimized version (if API supports filtering):**
```python
def api_source_optimized(dynamic_where=None, dynamic_columns=None):
    """API supports query parameters - use protocol!"""
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.example.com/products", params=params)
    for item in response.json():
        yield item

engine.register("products", api_source_optimized)  # Auto-detected!
```

### Example 4: MongoDB (Optimized)

```python
def mongo_source(dynamic_where=None, dynamic_columns=None):
    """MongoDB supports filters and projections."""
    collection = get_mongo_collection("products")
    
    # Convert WHERE to MongoDB filter
    filter_dict = {}
    if dynamic_where:
        # Parse SQL WHERE to MongoDB filter (simplified)
        filter_dict = parse_where_to_mongo(dynamic_where)
    
    # Convert columns to MongoDB projection
    projection = None
    if dynamic_columns:
        projection = {col: 1 for col in dynamic_columns}
    
    for doc in collection.find(filter_dict, projection):
        yield doc

engine.register("products", mongo_source)  # Auto-detected!
```

---

## Recommended Architecture

### ✅ DO: Pure Iterator Protocol

```python
# Core library: Just iterators
engine.register("table", source_function)

# If source_function accepts (dynamic_where, dynamic_columns):
#   → Optimizations apply automatically
# If not:
#   → Works normally, no optimizations
```

**Benefits:**
- ✅ Simple: One way to register sources
- ✅ Flexible: Works with any data source
- ✅ Automatic: No flags, engine detects capability
- ✅ Clean: No database dependencies in core

### ❌ DON'T: Database-Specific Code in Core

```python
# BAD: Database code in core library
from streaming_sql_engine import PostgreSQLPool, create_table_source
engine.register("users", create_table_source(pool, "users"), is_database_source=True)
```

**Problems:**
- ❌ Requires database libraries in core
- ❌ Harder to extend to new sources
- ❌ Flag is redundant (signature check already works)

---

## Implementation Plan

### Step 1: Remove `is_database_source` Flag

**Current code:**
```python
# executor.py
if root_metadata.get('is_database_source') and (root_required_columns or pushable_where_sql):
    # ... optimization code
```

**New code:**
```python
# executor.py - Just check signature, no flag needed
import inspect
sig = inspect.signature(root_source_fn)
if 'dynamic_where' in sig.parameters or 'dynamic_columns' in sig.parameters:
    # ... optimization code
```

### Step 2: Update Engine API

**Current:**
```python
engine.register("table", source_fn, is_database_source=True)
```

**New:**
```python
engine.register("table", source_fn)  # Flag removed!
```

### Step 3: Move Database Connectors to Examples

Move `db_connector.py` → `examples/database_helpers.py`

Users can copy/modify for their needs, or you can create optional package:
- `streaming-sql-engine` (core)
- `streaming-sql-engine-db` (optional database helpers)

---

## Summary: Best Approach

### **Pure Iterator Protocol**

1. **Everything is an iterator function**
   ```python
   def source() -> Iterator[Dict]:
       ...
   ```

2. **Optional optimization protocol**
   ```python
   def source(dynamic_where=None, dynamic_columns=None) -> Iterator[Dict]:
       # If you accept these params, optimizations apply
       ...
   ```

3. **Engine auto-detects**
   - Checks function signature
   - Applies optimizations if protocol supported
   - Falls back to normal execution if not

4. **No flags, no database code in core**
   - Clean separation of concerns
   - Easy to extend
   - Works with any data source

### Result

- ✅ Core library: Pure SQL execution, no database dependencies
- ✅ Users: Write iterators, get optimizations automatically if protocol followed
- ✅ Flexibility: Works with databases, files, APIs, anything
- ✅ Simplicity: One way to register sources

---

## Migration Guide

**Old way:**
```python
from streaming_sql_engine import create_table_source
engine.register("users", create_table_source(pool, "users"), is_database_source=True)
```

**New way:**
```python
# Option 1: Use helper from examples (copy to your project)
from examples.database_helpers import create_table_source
engine.register("users", create_table_source(pool, "users"))

# Option 2: Write your own (follows protocol automatically)
def my_db_source(dynamic_where=None, dynamic_columns=None):
    # ... your database code
    return iterator
engine.register("users", my_db_source)  # Auto-detected!
```

