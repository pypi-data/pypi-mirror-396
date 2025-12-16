# Final Implementation Recommendations

## Executive Summary

**Goal:** Make the library cleaner, more flexible, and correctly architected.

**Key Changes:**

1. Remove database connectors from core
2. Make optimizations protocol-based (not database-based)
3. Keep Polars as optional optimization
4. Move database helpers to examples

---

## 1. Core Architecture Changes

### ✅ Remove Database Dependencies from Core

**Action:**

- Move `db_connector.py` → `examples/database_helpers.py`
- Remove database imports from `__init__.py`
- Remove database dependencies from `pyproject.toml` core dependencies

**Why:**

- Separation of concerns (SQL execution ≠ database connectivity)
- Minimal dependencies (only `sqlglot` required)
- Users can choose their database library

**Impact:**

- ✅ Core library is lighter
- ✅ No database dependencies required
- ✅ More flexible

---

### ✅ Remove `is_database_source` Flag

**Action:**

- Remove `is_database_source` parameter from `Engine.register()`
- Update executor to use protocol detection only

**Why:**

- Flag is redundant (protocol detection already works)
- Optimizations aren't database-specific (work with APIs, files, etc.)
- Simpler API (one less parameter)

**Impact:**

- ✅ Cleaner API
- ✅ Optimizations work with any source
- ✅ Automatic detection

---

### ✅ Implement Pure Protocol Detection

**Action:**

- Update `executor.py` to check function signature
- Remove flag-based checks
- Document protocol for users

**Code Change:**

```python
# executor.py - NEW
import inspect

def source_supports_optimizations(source_fn):
    """Check if source implements optimization protocol."""
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())
    return 'dynamic_where' in params or 'dynamic_columns' in params

# Use protocol detection
if source_supports_optimizations(root_source_fn):
    # Apply optimizations - works with ANY source!
    ...
```

**Why:**

- Correct architecture (protocol-based, not type-based)
- Works with databases, APIs, files, custom sources
- Automatic detection (no flags needed)

**Impact:**

- ✅ Optimizations work with any source
- ✅ Correct architecture
- ✅ More flexible

---

## 2. File Structure Changes

### Current Structure

```
streaming_sql_engine/
├── __init__.py          # Exports Engine + DB connectors
├── engine.py
├── executor.py
├── db_connector.py      # ← Remove from core
└── ...
```

### Recommended Structure

```
streaming_sql_engine/
├── __init__.py          # Only exports Engine
├── engine.py
├── executor.py
├── ... (core modules)
└── (NO db_connector.py)

examples/
└── database_helpers.py  # ← Move here (reference implementations)
```

---

## 3. API Changes

### Current API

```python
from streaming_sql_engine import Engine, create_table_source

engine = Engine()
engine.register(
    "users",
    create_table_source(pool, "users"),
    is_database_source=True  # ← Remove this flag
)
```

### Recommended API

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_postgresql_source  # Or write your own

engine = Engine()
engine.register(
    "users",
    create_postgresql_source(pool, "users")
    # No flag needed! Protocol detected automatically
)
```

**Benefits:**

- ✅ Simpler API (one less parameter)
- ✅ Automatic detection
- ✅ Works with any source

---

## 4. Dependency Changes

### Current Dependencies

```python
# pyproject.toml
dependencies = [
    "sqlglot>=23.0.0",
    "psycopg2-binary>=2.9.0",  # ← Remove
    "pymysql>=1.0.0",          # ← Remove
    "pymongo>=...",             # ← Remove
    ...
]
```

### Recommended Dependencies

```python
# pyproject.toml - Core
dependencies = [
    "sqlglot>=23.0.0",  # Only SQL parsing required
]

# Optional dependencies
[project.optional-dependencies]
polars = ["polars>=0.19.0"]  # For Polars optimizations
dev = ["pytest", "black", ...]
```

**Benefits:**

- ✅ Minimal core dependencies
- ✅ Users install what they need
- ✅ No database dependencies required

---

## 5. Implementation Checklist

### Phase 1: Protocol Detection (Backward Compatible)

- [ ] **Update `executor.py`**

  - [ ] Add `source_supports_optimizations()` function
  - [ ] Check protocol first, fall back to flag for compatibility
  - [ ] Test with protocol-based sources
  - [ ] Test with flag-based sources (backward compatibility)

- [ ] **Update `engine.py`**

  - [ ] Keep `is_database_source` parameter (deprecated)
  - [ ] Add deprecation warning
  - [ ] Document protocol in docstring

- [ ] **Update documentation**
  - [ ] Document protocol
  - [ ] Add examples for APIs, files, custom sources
  - [ ] Migration guide

### Phase 2: Move Database Code

- [ ] **Create `examples/database_helpers.py`**

  - [ ] Copy `db_connector.py` content
  - [ ] Add examples and documentation
  - [ ] Show protocol implementation

- [ ] **Update `__init__.py`**

  - [ ] Remove database imports
  - [ ] Only export `Engine`
  - [ ] Update `__all__`

- [ ] **Update `pyproject.toml`**
  - [ ] Remove database dependencies
  - [ ] Keep only `sqlglot`
  - [ ] Add optional `polars` dependency

### Phase 3: Clean Up (Breaking Changes)

- [ ] **Remove `is_database_source` flag**

  - [ ] Remove parameter from `Engine.register()`
  - [ ] Remove flag checks from executor
  - [ ] Update all examples

- [ ] **Update documentation**

  - [ ] Remove references to flag
  - [ ] Update all examples to use protocol
  - [ ] Add migration guide

- [ ] **Version bump**
  - [ ] Major version bump (breaking changes)
  - [ ] Update CHANGELOG
  - [ ] Migration guide in README

---

## 6. Code Examples

### Example 1: Database Source (Using Helper)

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_postgresql_source

engine = Engine()
engine.register("users", create_postgresql_source(pool, "users"))
# Optimizations apply automatically via protocol!
```

### Example 2: Custom Database Source

```python
from streaming_sql_engine import Engine

def my_db_source(dynamic_where=None, dynamic_columns=None):
    """Custom database source - follows protocol."""
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""

    query = f"SELECT {', '.join(columns)} FROM users"
    if where:
        query += f" WHERE {where}"

    for row in execute(query):
        yield row

engine = Engine()
engine.register("users", my_db_source)
# Optimizations apply automatically!
```

### Example 3: REST API Source

```python
from streaming_sql_engine import Engine

def api_source(dynamic_where=None, dynamic_columns=None):
    """REST API source - follows protocol."""
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)

    response = requests.get("https://api.com/data", params=params)
    for item in response.json():
        yield item

engine = Engine()
engine.register("data", api_source)
# Optimizations apply automatically!
```

### Example 4: File Source (No Protocol)

```python
from streaming_sql_engine import Engine

def file_source():
    """Simple file source - no protocol."""
    with open("data.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine = Engine()
engine.register("data", file_source)
# Works fine, no optimizations (that's OK!)
```

---

## 7. Testing Strategy

### Test Protocol Detection

```python
def test_protocol_detection():
    # Test with protocol
    def protocol_source(dynamic_where=None, dynamic_columns=None):
        ...

    assert source_supports_optimizations(protocol_source) == True

    # Test without protocol
    def simple_source():
        ...

    assert source_supports_optimizations(simple_source) == False
```

### Test Optimizations

```python
def test_filter_pushdown():
    # Source with protocol
    def source(dynamic_where=None, dynamic_columns=None):
        assert dynamic_where == "id > 100"
        ...

    engine.register("users", source)
    engine.query("SELECT * FROM users WHERE users.id > 100")
    # Verify source was called with dynamic_where
```

### Test Backward Compatibility

```python
def test_backward_compatibility():
    # Old code with flag should still work (Phase 1)
    engine.register("users", source, is_database_source=True)
    # Should work with deprecation warning
```

---

## 8. Documentation Updates

### Update README

- [ ] Remove database connector examples from main README
- [ ] Add protocol examples
- [ ] Link to `examples/database_helpers.py`
- [ ] Show API, file, custom source examples

### Update API Documentation

- [ ] Document protocol in `Engine.register()` docstring
- [ ] Remove `is_database_source` from parameters
- [ ] Add protocol examples
- [ ] Migration guide

### Create Examples Directory

- [ ] `examples/database_helpers.py` - Database reference implementations
- [ ] `examples/api_source.py` - REST API example
- [ ] `examples/file_source.py` - File source example
- [ ] `examples/custom_source.py` - Custom source example

---

## 9. Migration Guide for Users

### For Users Using Database Connectors

**Old way:**

```python
from streaming_sql_engine import Engine, create_table_source

engine = Engine()
engine.register("users", create_table_source(pool, "users"), is_database_source=True)
```

**New way (Option 1 - Use helper):**

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_postgresql_source

engine = Engine()
engine.register("users", create_postgresql_source(pool, "users"))
```

**New way (Option 2 - Write your own):**

```python
from streaming_sql_engine import Engine

def my_source(dynamic_where=None, dynamic_columns=None):
    # Your implementation
    ...

engine = Engine()
engine.register("users", my_source)
```

---

## 10. Benefits Summary

### ✅ Cleaner Architecture

- Separation of concerns
- Core focused on SQL execution
- Database code separate

### ✅ More Flexible

- Works with any source type
- Protocol-based (not type-based)
- Easy to extend

### ✅ Minimal Dependencies

- Core: Only `sqlglot`
- Optional: Polars
- No database dependencies

### ✅ Better API

- Simpler (no flags)
- Automatic detection
- Protocol-based

### ✅ Same Functionality

- Optimizations still work
- Database helpers available
- Polars still works

---

## 11. Risk Assessment

### Low Risk Changes

- ✅ Protocol detection (additive, doesn't break existing code)
- ✅ Moving database code to examples (users can still use it)
- ✅ Documentation updates

### Medium Risk Changes

- ⚠️ Removing `is_database_source` flag (breaking change)
- ⚠️ Removing database imports from `__init__.py` (breaking change)

### Mitigation

- Phase 1: Add protocol, keep flag (backward compatible)
- Phase 2: Move database code (users can still import from examples)
- Phase 3: Remove flag (major version bump, migration guide)

---

## 12. Timeline Recommendation

### Week 1: Phase 1 (Protocol Detection)

- Implement protocol detection
- Keep flag for compatibility
- Test thoroughly
- Update documentation

### Week 2: Phase 2 (Move Database Code)

- Create examples directory
- Move database helpers
- Update imports
- Test examples

### Week 3: Phase 3 (Clean Up)

- Remove flag
- Final testing
- Update all documentation
- Release major version

---

## Final Recommendation Summary

### ✅ DO

1. **Remove database connectors from core**

   - Move to `examples/database_helpers.py`
   - Keep as reference implementations

2. **Remove `is_database_source` flag**

   - Use protocol detection instead
   - Simpler API

3. **Implement pure protocol detection**

   - Check function signature
   - Works with any source

4. **Keep Polars as optional**

   - Already works well
   - Auto-detected

5. **Minimal dependencies**
   - Core: Only `sqlglot`
   - Optional: Polars

### ❌ DON'T

1. **Don't remove optimizations**

   - They're valuable
   - Just make them protocol-based

2. **Don't break backward compatibility immediately**

   - Phase approach (add protocol, then remove flag)

3. **Don't force database dependencies**
   - Make them optional
   - Users choose

---

## Conclusion

**Recommended approach:**

1. ✅ Remove database connectors from core
2. ✅ Make optimizations protocol-based
3. ✅ Keep Polars as optional
4. ✅ Move database helpers to examples

**Result:**

- Cleaner architecture
- More flexible
- Minimal dependencies
- Same functionality
- Better API

**Implementation:**

- Phase 1: Add protocol (backward compatible)
- Phase 2: Move database code
- Phase 3: Remove flag (breaking change)

This makes the library:

- ✅ Focused on SQL execution
- ✅ Flexible with any source
- ✅ Easy to extend
- ✅ Correctly architected
