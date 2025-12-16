# Final Recommendation: What to Do

## Recommendation: **Remove DB Connectors, Keep Optimizations**

### Why?

1. **Separation of Concerns**
   - Core library = SQL execution only
   - Database connectivity = Not core responsibility

2. **Optimizations Are NOT Database-Specific**
   - Work with APIs, files, any source
   - Protocol-based, not database-based

3. **Minimal Dependencies**
   - Core: Only `sqlglot` required
   - No database libraries in core

4. **Flexibility**
   - Users choose their database library
   - Easy to extend to new sources

---

## What to Do

### ✅ KEEP: Optimizations (Protocol-Based)

**Keep optimizations, but make them protocol-based (not database-based):**

```python
# executor.py - NEW approach
import inspect

def should_apply_optimizations(source_fn):
    """Check if source supports optimizations via protocol."""
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())
    
    # Protocol: If function accepts these parameters, optimizations apply
    return 'dynamic_where' in params or 'dynamic_columns' in params

# Use protocol detection
if should_apply_optimizations(source_fn):
    # Apply filter pushdown and column pruning
    # Works with databases, APIs, files, ANY source!
    ...
```

**Benefits:**
- ✅ Works with databases
- ✅ Works with APIs
- ✅ Works with files
- ✅ Works with custom sources

---

### ❌ REMOVE: Database Connectors from Core

**Move `db_connector.py` to examples:**

```
streaming_sql_engine/
├── engine.py
├── executor.py
├── ... (core modules)
└── (NO db_connector.py)

examples/
└── database_helpers.py  # ← Move here
```

**Or create separate optional package:**

```
streaming-sql-engine/          # Core (no database code)
streaming-sql-engine-db/       # Optional database helpers
```

---

## Implementation Plan

### Step 1: Update Executor (Protocol Detection)

**Current code:**
```python
# executor.py
if root_metadata.get('is_database_source') and (root_required_columns or pushable_where_sql):
    # Apply optimizations
    ...
```

**New code:**
```python
# executor.py
import inspect

def source_supports_optimizations(source_fn):
    """Check if source implements optimization protocol."""
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())
    return 'dynamic_where' in params or 'dynamic_columns' in params

# Apply optimizations based on protocol, not flag
if source_supports_optimizations(root_source_fn) and (root_required_columns or pushable_where_sql):
    # Apply optimizations - works with ANY source!
    ...
```

---

### Step 2: Update Engine API (Remove Flag)

**Current code:**
```python
# engine.py
def register(
    self,
    table_name,
    source_fn,
    ordered_by=None,
    is_database_source=False,  # ← Remove this
    filename=None
):
    ...
```

**New code:**
```python
# engine.py
def register(
    self,
    table_name,
    source_fn,
    ordered_by=None,      # Keep (for merge joins)
    filename=None         # Keep (for mmap joins)
):
    # Remove is_database_source parameter
    # Engine detects protocol automatically
    ...
```

---

### Step 3: Move Database Connectors

**Option A: Move to Examples (Recommended)**

```python
# examples/database_helpers.py
"""
Database helper functions - reference implementations.
Users can copy/modify for their needs.
"""

def create_postgresql_source(pool, table_name, **kwargs):
    """Example: PostgreSQL source with optimizations."""
    def source_fn(dynamic_where=None, dynamic_columns=None):
        # PostgreSQL implementation
        ...
    return source_fn

def create_mysql_source(pool, table_name, **kwargs):
    """Example: MySQL source with optimizations."""
    ...

def create_mongo_source(pool, collection_name, **kwargs):
    """Example: MongoDB source with optimizations."""
    ...
```

**Option B: Separate Package (Advanced)**

```python
# streaming-sql-engine-db/__init__.py
from streaming_sql_engine import Engine

def create_postgresql_source(...):
    ...

def create_mysql_source(...):
    ...

# Users install separately:
# pip install streaming-sql-engine
# pip install streaming-sql-engine-db
```

---

### Step 4: Update `__init__.py` (Remove DB Imports)

**Current code:**
```python
# __init__.py
from .engine import Engine
from .db_connector import (
    PostgreSQLPool,
    MySQLPool,
    MongoPool,
    create_table_source,
    ...
)
```

**New code:**
```python
# __init__.py
from .engine import Engine

__all__ = ["Engine"]
# No database imports - keep core clean!
```

---

## Migration Guide for Users

### Old Way (With Flag)

```python
from streaming_sql_engine import Engine, create_table_source

engine = Engine()
engine.register(
    "users",
    create_table_source(pool, "users"),
    is_database_source=True  # ← Flag needed
)
```

### New Way (Protocol-Based)

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_postgresql_source  # Or copy to your code

engine = Engine()
engine.register(
    "users",
    create_postgresql_source(pool, "users")
    # No flag needed! Protocol detected automatically
)
```

**Or write your own:**

```python
def my_db_source(dynamic_where=None, dynamic_columns=None):
    """Your database source - follows protocol."""
    query = build_query(dynamic_where, dynamic_columns)
    for row in execute(query):
        yield row

engine.register("users", my_db_source)
# Optimizations apply automatically!
```

---

## What Users Get

### ✅ Still Get Optimizations

**Optimizations still work** - just protocol-based instead of flag-based:

```python
# Any source that implements protocol gets optimizations
def api_source(dynamic_where=None, dynamic_columns=None):
    # API implementation
    ...

def db_source(dynamic_where=None, dynamic_columns=None):
    # Database implementation
    ...

def file_source(dynamic_where=None, dynamic_columns=None):
    # File implementation
    ...

# All get optimizations automatically!
engine.register("api_data", api_source)
engine.register("db_data", db_source)
engine.register("file_data", file_source)
```

### ✅ Database Helpers Available

**Database helpers moved to examples** - users can:
- Copy and modify
- Use as reference
- Create their own

---

## Benefits Summary

### ✅ Cleaner Core
- No database dependencies
- Focused on SQL execution
- Easier to maintain

### ✅ More Flexible
- Works with any source type
- Users choose their database library
- Easy to extend

### ✅ Same Functionality
- Optimizations still work
- Database helpers available (in examples)
- Protocol-based (better than flags)

### ✅ Better Architecture
- Separation of concerns
- Protocol-based (not type-based)
- Minimal dependencies

---

## Final Answer

### **Remove DB Connectors, Keep Optimizations**

**What to remove:**
- ❌ `db_connector.py` from core
- ❌ `is_database_source` flag
- ❌ Database imports from `__init__.py`

**What to keep:**
- ✅ Optimizations (filter pushdown, column pruning)
- ✅ Protocol-based detection
- ✅ Database helpers (move to examples)

**Result:**
- Cleaner core library
- Optimizations work with ANY source
- Database helpers available as examples
- Better architecture

---

## Implementation Checklist

- [ ] Update executor to use protocol detection
- [ ] Remove `is_database_source` flag from engine
- [ ] Move `db_connector.py` to `examples/database_helpers.py`
- [ ] Update `__init__.py` to remove database imports
- [ ] Update documentation with protocol examples
- [ ] Add migration guide for users
- [ ] Test with database sources (using examples)
- [ ] Test with API sources (protocol-based)
- [ ] Test with file sources (protocol-based)

---

## Example: Complete Refactored Code

### Core Library (`streaming_sql_engine/`)

```python
# engine.py - Clean API
class Engine:
    def register(self, table_name, source_fn, ordered_by=None, filename=None):
        # No is_database_source flag!
        # Protocol detected automatically
        ...

# executor.py - Protocol-based
def execute_plan(...):
    if source_supports_optimizations(source_fn):
        # Apply optimizations - works with ANY source!
        ...
```

### Examples (`examples/database_helpers.py`)

```python
# Reference implementations users can copy/modify
def create_postgresql_source(pool, table, **kwargs):
    def source_fn(dynamic_where=None, dynamic_columns=None):
        # PostgreSQL implementation with optimizations
        ...
    return source_fn
```

### User Code

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_postgresql_source

engine = Engine()
engine.register("users", create_postgresql_source(pool, "users"))
# Optimizations apply automatically via protocol!
```

---

## Summary

**Remove:** Database connectors from core  
**Keep:** Optimizations (make them protocol-based)  
**Move:** Database helpers to examples  
**Result:** Cleaner, more flexible, same functionality

