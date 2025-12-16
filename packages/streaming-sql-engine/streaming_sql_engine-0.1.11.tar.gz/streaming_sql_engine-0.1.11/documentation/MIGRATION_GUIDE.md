# Migration Guide: Protocol-Based Architecture

## Overview

The library has been refactored to use **protocol-based optimization detection** instead of flags. This makes the API simpler and enables optimizations for any source type (databases, APIs, files, etc.).

---

## What Changed

### ✅ Removed

- `is_database_source` flag from `Engine.register()`
- Database connectors from core library (`db_connector.py`)
- Database dependencies from core (`psycopg2`, `pymysql`, `pymongo`)

### ✅ Added

- Protocol-based optimization detection (automatic)
- Database helpers in `examples/database_helpers.py`
- Optional database dependencies (`pip install streaming-sql-engine[db]`)

---

## Migration Steps

### Step 1: Update Imports

**Old:**

```python
from streaming_sql_engine import Engine, create_table_source, create_pool_from_env
```

**New:**

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_table_source, create_pool_from_env
```

### Step 2: Remove `is_database_source` Flag

**Old:**

```python
engine = Engine()
engine.register(
    "users",
    create_table_source(pool, "users"),
    is_database_source=True  # ← Remove this!
)
```

**New:**

```python
engine = Engine()
engine.register(
    "users",
    create_table_source(pool, "users")
    # No flag needed! Protocol detected automatically
)
```

### Step 3: Install Database Dependencies (If Needed)

**Old:**

```bash
pip install streaming-sql-engine
# Database dependencies included automatically
```

**New:**

```bash
# Core only (no database dependencies)
pip install streaming-sql-engine

# With database helpers (optional)
pip install streaming-sql-engine[db]
```

---

## Examples

### Example 1: PostgreSQL Source

**Old:**

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source

pool = create_pool_from_env()
engine = Engine()

engine.register(
    "users",
    create_table_source(pool, "users", order_by="id"),
    ordered_by="id",
    is_database_source=True  # ← Remove
)
```

**New:**

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_pool_from_env, create_table_source

pool = create_pool_from_env()
engine = Engine()

engine.register(
    "users",
    create_table_source(pool, "users", order_by="id"),
    ordered_by="id"
    # Protocol detected automatically!
)
```

### Example 2: Custom Database Source

**Old:**

```python
def my_db_source():
    # Custom database implementation
    ...

engine.register("users", my_db_source, is_database_source=True)
```

**New:**

```python
def my_db_source(dynamic_where=None, dynamic_columns=None):
    """Implement protocol for optimizations."""
    # Build query with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""

    query = f"SELECT {', '.join(columns)} FROM users"
    if where:
        query += f" WHERE {where}"

    for row in execute(query):
        yield row

engine.register("users", my_db_source)
# Protocol detected automatically!
```

### Example 3: REST API Source (Now Gets Optimizations!)

**Old:**

```python
def api_source():
    # API implementation
    ...

engine.register("products", api_source)
# No optimizations (flag was database-only)
```

**New:**

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    """API source with protocol - gets optimizations!"""
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)

    response = requests.get("https://api.com/products", params=params)
    for item in response.json():
        yield item

engine.register("products", api_source)
# Optimizations apply automatically! (Not possible before)
```

---

## Benefits

### ✅ Simpler API

- No flags to remember
- Automatic detection
- Cleaner code

### ✅ More Flexible

- Works with any source type
- APIs can get optimizations
- Files can get optimizations
- Custom sources can get optimizations

### ✅ Better Architecture

- Protocol-based (not type-based)
- Separation of concerns
- Minimal dependencies

---

## Backward Compatibility

**Note:** This is a **breaking change**. Existing code using `is_database_source` flag will need to be updated.

**Migration is straightforward:**

1. Remove `is_database_source=True` from `register()` calls
2. Update imports to use `examples.database_helpers`
3. That's it!

**Optimizations still work** - they're just detected automatically now.

---

## Questions?

### Q: Do I need to change my source functions?

**A:** Only if you want optimizations. If your source function accepts `dynamic_where` and/or `dynamic_columns` parameters, optimizations apply automatically.

### Q: Will my existing code break?

**A:** Yes, if it uses `is_database_source` flag. Update imports and remove the flag.

### Q: Do optimizations still work?

**A:** Yes! They're detected automatically via protocol. Same performance, simpler API.

### Q: Can I still use database helpers?

**A:** Yes! They're in `examples/database_helpers.py`. Copy/modify as needed.

---

## Summary

**Changes:**

- ✅ Remove `is_database_source` flag
- ✅ Update imports to `examples.database_helpers`
- ✅ Protocol detection is automatic

**Result:**

- ✅ Simpler API
- ✅ More flexible
- ✅ Same performance
- ✅ Better architecture
