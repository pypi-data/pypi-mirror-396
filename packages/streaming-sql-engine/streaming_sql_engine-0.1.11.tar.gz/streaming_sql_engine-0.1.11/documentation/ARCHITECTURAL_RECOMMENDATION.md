# Architectural Recommendation: How the Library Should Be

## Core Principle

**"Pure SQL execution engine with iterator-based sources. Everything else is optional."**

---

## Recommended Structure

### 1. **Core Library** (`streaming-sql-engine`)

**Purpose:** Pure SQL execution - parsing, planning, optimization, execution

**Dependencies (minimal):**
- `sqlglot` - SQL parsing (required)
- `polars` - Optional optimization (auto-detected)

**NO database dependencies:**
- ❌ No `psycopg2`
- ❌ No `pymysql`
- ❌ No `pymongo`
- ❌ No database-specific code

**Core API:**
```python
from streaming_sql_engine import Engine

engine = Engine()
engine.register("table", source_function)  # Just iterators!
results = engine.query("SELECT ...")
```

---

## Architecture Layers

### Layer 1: Core Engine (Required)

```
streaming_sql_engine/
├── __init__.py          # Only exports Engine
├── engine.py            # Public API
├── parser.py            # SQL parsing (sqlglot)
├── planner.py           # Logical planning
├── optimizer.py          # Query optimization
├── executor.py           # Execution pipeline
├── jsonl_executor.py     # Alternative executor
├── evaluator.py          # Expression evaluation
├── operators.py          # Iterator operators (Python)
└── polars_operators.py   # Polars operators (optional)
```

**Key characteristics:**
- ✅ Pure Python + sqlglot
- ✅ Iterator-based (no assumptions about sources)
- ✅ Protocol-based optimization detection
- ✅ No database code

---

### Layer 2: Optional Optimizations (Auto-detected)

**Mmap joins** (for large files):
```
streaming_sql_engine/
├── operators_mmap.py     # Mmap-based joins (optional)
└── mmap_index.py        # Position index (optional)
```

**Polars** (for speed):
```
streaming_sql_engine/
└── polars_operators.py   # Already exists, auto-detected
```

**How it works:**
- Engine tries to import optional modules
- If available → uses them
- If not → falls back to Python
- **No user configuration needed**

---

### Layer 3: Helper Libraries (Separate Packages)

**Database connectors** → Move to separate package or examples:

```
streaming-sql-engine-db/  # Optional package
├── postgresql.py
├── mysql.py
└── mongodb.py

# OR

examples/
└── database_helpers.py   # Reference implementations
```

**Why separate:**
- Users who don't need databases don't install database dependencies
- Users can choose their database library
- Easy to extend with new database types

---

## API Design

### Simplified `register()` Method

**Current (has flags):**
```python
engine.register(
    "table",
    source_fn,
    ordered_by="id",
    is_database_source=True,  # ← Remove this
    filename="file.jsonl"
)
```

**Recommended (protocol-based):**
```python
engine.register(
    "table",
    source_fn,
    ordered_by="id",      # For merge joins
    filename="file.jsonl"  # For mmap joins
)
```

**Removed:**
- ❌ `is_database_source` flag (redundant - use protocol detection)

**Protocol detection:**
```python
# Engine automatically detects if source supports optimizations
def source(dynamic_where=None, dynamic_columns=None):
    # If function accepts these → optimizations apply
    ...
```

---

## Source Protocol

### Simple Iterator (No Optimizations)

```python
def simple_source():
    """Returns iterator of dicts."""
    return iter([{"id": 1, "name": "Alice"}])

engine.register("users", simple_source)
# Works perfectly, no optimizations
```

### Optimized Iterator (With Protocol)

```python
def optimized_source(dynamic_where=None, dynamic_columns=None):
    """
    Protocol: Accept these parameters to enable optimizations.
    
    Args:
        dynamic_where: SQL WHERE clause string
        dynamic_columns: List of column names
    
    Returns:
        Iterator of dicts
    """
    # Build query with optimizations
    query = build_query(dynamic_where, dynamic_columns)
    for row in execute(query):
        yield row

engine.register("users", optimized_source)
# Engine auto-detects protocol → optimizations apply!
```

---

## Module Responsibilities

### Core Modules

| Module | Responsibility | Dependencies |
|--------|---------------|--------------|
| `engine.py` | Public API, source registration | None |
| `parser.py` | SQL → AST | sqlglot |
| `planner.py` | AST → Logical plan | sqlglot |
| `optimizer.py` | Column pruning, filter pushdown | None |
| `executor.py` | Build iterator pipeline | None |
| `evaluator.py` | Expression evaluation | sqlglot |
| `operators.py` | Python iterator operators | None |

### Optional Modules

| Module | Responsibility | When Used |
|--------|---------------|-----------|
| `polars_operators.py` | Polars-based operators | If polars installed |
| `operators_mmap.py` | Mmap-based joins | If filename provided |
| `mmap_index.py` | Position index | If filename provided |
| `jsonl_executor.py` | JSONL export/merge | If use_jsonl_mode=True |

---

## Dependency Management

### Core Dependencies (Required)

```python
# pyproject.toml
[project]
dependencies = [
    "sqlglot>=23.0.0",  # SQL parsing (required)
]
```

### Optional Dependencies

```python
[project.optional-dependencies]
polars = ["polars>=0.19.0"]  # For Polars optimizations
dev = ["pytest", "black", ...]
```

**Users install what they need:**
```bash
# Core only
pip install streaming-sql-engine

# With Polars
pip install streaming-sql-engine[polars]

# Database helpers (separate package)
pip install streaming-sql-engine-db
```

---

## Execution Strategy Selection

### Automatic Selection (No User Configuration)

```python
# Engine automatically selects best strategy:

1. Merge Join
   └─ If: Both sides sorted (ordered_by provided)
   └─ Why: O(n+m), minimal memory

2. Mmap Join
   └─ If: Filename provided, mmap available
   └─ Why: Lowest memory (90-99% reduction)

3. Polars Join
   └─ If: Polars installed, table large enough
   └─ Why: Fastest (10-200x speedup)

4. Python Join
   └─ If: None of above
   └─ Why: Always works (fallback)
```

**User doesn't need to choose** - engine picks best option automatically!

---

## Migration Path

### Phase 1: Refactor Core (Backward Compatible)

1. **Update executor** to use protocol detection instead of flag
   ```python
   # Still check flag for backward compatibility
   # But also check function signature
   if is_database_source or function_accepts_protocol():
       apply_optimizations()
   ```

2. **Deprecate `is_database_source`** flag
   ```python
   def register(..., is_database_source=False):
       if is_database_source:
           warnings.warn("is_database_source is deprecated, use protocol instead")
   ```

### Phase 2: Move Database Code

1. **Create `examples/database_helpers.py`**
   - Copy `db_connector.py` content
   - Add examples and documentation

2. **Update `__init__.py`**
   ```python
   # Remove database imports from core
   # Keep only Engine
   from .engine import Engine
   __all__ = ["Engine"]
   ```

### Phase 3: Clean Up (Breaking Changes)

1. **Remove `is_database_source`** flag completely
2. **Remove database code** from core
3. **Update documentation** with protocol examples

---

## Example: Complete Refactored API

### User Code (Simple)

```python
from streaming_sql_engine import Engine

# Create engine
engine = Engine()

# Register sources (just iterators!)
def users_source():
    return iter([{"id": 1, "name": "Alice"}])

def orders_source():
    return iter([{"id": 1, "user_id": 1, "total": 100}])

engine.register("users", users_source)
engine.register("orders", orders_source)

# Query
for row in engine.query("""
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
"""):
    print(row)
```

### User Code (With Optimizations)

```python
from streaming_sql_engine import Engine

engine = Engine()

# Optimized source (follows protocol)
def db_source(dynamic_where=None, dynamic_columns=None):
    # Build query with optimizations
    query = build_query(dynamic_where, dynamic_columns)
    for row in execute(query):
        yield row

# File source with mmap
def file_source():
    with open("large.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", db_source)  # Auto-detects protocol!
engine.register("images", file_source, filename="large.jsonl")  # Auto-enables mmap!

# Query - optimizations apply automatically!
for row in engine.query("SELECT ..."):
    print(row)
```

### Database Helpers (Optional, in Examples)

```python
# examples/database_helpers.py
from streaming_sql_engine import Engine

def create_postgresql_source(pool, table, **kwargs):
    """Helper function - users can copy/modify."""
    def source(dynamic_where=None, dynamic_columns=None):
        # PostgreSQL implementation
        ...
    return source

# Usage
from examples.database_helpers import create_postgresql_source
engine.register("users", create_postgresql_source(pool, "users"))
```

---

## Benefits of This Architecture

### ✅ **Separation of Concerns**
- Core: SQL execution only
- Database: Separate package/examples
- Optimizations: Auto-detected

### ✅ **Minimal Dependencies**
- Core: Only sqlglot
- Optional: Polars, database libraries
- Users install what they need

### ✅ **Flexibility**
- Works with any data source
- Easy to extend
- No assumptions about sources

### ✅ **Simplicity**
- One way to register sources
- Automatic optimization detection
- No flags or configuration

### ✅ **Performance**
- Multiple optimization strategies
- Automatic selection
- Falls back gracefully

---

## Summary: Recommended Structure

```
streaming-sql-engine/          # Core package
├── Core engine (SQL execution)
├── Optional optimizations (auto-detected)
└── No database code

streaming-sql-engine-db/       # Optional package (or examples/)
└── Database helpers

User code:
├── Install core: pip install streaming-sql-engine
├── Optional: pip install streaming-sql-engine[polars]
├── Optional: pip install streaming-sql-engine-db
└── Write iterators → register → query
```

**Key principles:**
1. **Pure iterator protocol** - everything is an iterator
2. **Protocol-based optimization** - auto-detected, no flags
3. **Minimal core** - SQL execution only
4. **Optional extras** - Polars, mmap, database helpers
5. **Automatic selection** - engine picks best strategy

This makes the library:
- ✅ Simple to use
- ✅ Easy to extend
- ✅ Lightweight (minimal dependencies)
- ✅ Flexible (works with any source)
- ✅ Performant (multiple optimization strategies)

