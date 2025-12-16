# Protocol Detection and Optimizations Explained

## What is "Protocol Detection"?

**Protocol detection** = Engine automatically checks if your source function accepts optimization parameters by looking at its function signature.

### How It Works

The engine uses Python's `inspect.signature()` to check your function:

```python
import inspect

def check_protocol(source_fn):
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())
    
    # Check if function accepts optimization parameters
    has_where = 'dynamic_where' in params
    has_columns = 'dynamic_columns' in params
    
    return has_where or has_columns
```

### Example: Two Different Sources

**Source 1: Simple (No Protocol)**
```python
def simple_source():
    """No optimization parameters - just returns iterator."""
    return iter([
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ])

# Engine checks: Does simple_source accept dynamic_where? NO
# Engine checks: Does simple_source accept dynamic_columns? NO
# Result: No optimizations, works normally
```

**Source 2: With Protocol (Optimized)**
```python
def optimized_source(dynamic_where=None, dynamic_columns=None):
    """Accepts optimization parameters - engine will use them!"""
    # Build query with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM users"
    if where:
        query += f" WHERE {where}"
    
    # Execute query and return iterator
    cursor = execute(query)
    for row in cursor:
        yield dict(row)

# Engine checks: Does optimized_source accept dynamic_where? YES ✅
# Engine checks: Does optimized_source accept dynamic_columns? YES ✅
# Result: Optimizations will be applied!
```

---

## What Are "Optimizations"?

Optimizations are **two performance improvements** the engine can apply:

### 1. **Filter Pushdown** (`dynamic_where`)

**What it does:** Pushes WHERE clause to the source instead of filtering in Python.

**Example:**

```python
# Query
query = "SELECT * FROM users WHERE users.id > 100"

# WITHOUT optimization (simple source):
def simple_source():
    # Fetches ALL rows from database
    return execute("SELECT * FROM users")  # Gets 1,000,000 rows

# Engine then filters in Python:
for row in simple_source():
    if row['id'] > 100:  # Filtering in Python (slow!)
        yield row

# WITH optimization (protocol source):
def optimized_source(dynamic_where=None, dynamic_columns=None):
    query = "SELECT * FROM users"
    if dynamic_where:  # Engine passes: "users.id > 100"
        query += f" WHERE {dynamic_where}"
    return execute(query)  # Database filters: Gets only 500 rows!

# Engine calls: optimized_source(dynamic_where="users.id > 100")
# Database does the filtering → Much faster!
```

**Benefits:**
- ✅ Less data transferred (database filters before sending)
- ✅ Faster (database uses indexes)
- ✅ Less memory (fewer rows in Python)

### 2. **Column Pruning** (`dynamic_columns`)

**What it does:** Only fetches columns needed for the query.

**Example:**

```python
# Query
query = "SELECT users.name FROM users JOIN orders ON users.id = orders.user_id"

# WITHOUT optimization (simple source):
def simple_source():
    # Fetches ALL columns
    return execute("SELECT * FROM users")  # Gets: id, name, email, password, address, phone, ...

# Each row: {"id": 1, "name": "Alice", "email": "...", "password": "...", ...}
# Engine only uses "name" but fetched everything!

# WITH optimization (protocol source):
def optimized_source(dynamic_where=None, dynamic_columns=None):
    columns = dynamic_columns or ["*"]  # Engine passes: ["id", "name"]
    query = f"SELECT {', '.join(columns)} FROM users"
    return execute(query)  # Database only selects: id, name

# Engine calls: optimized_source(dynamic_columns=["id", "name"])
# Each row: {"id": 1, "name": "Alice"}  ← Only needed columns!
```

**Benefits:**
- ✅ Less data transferred (only needed columns)
- ✅ Less memory (smaller rows)
- ✅ Faster I/O (less data to read)

---

## Complete Example: How It All Works Together

### Step 1: User Writes Query

```python
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
    WHERE users.id > 100
"""
```

### Step 2: Engine Analyzes Query

```python
# Engine's optimizer determines:
required_columns = {
    "users": {"id", "name"},      # Only need id and name from users
    "orders": {"user_id", "total"} # Only need user_id and total from orders
}

pushable_where = "users.id > 100"  # Can push to users table
```

### Step 3: Engine Checks Source Protocol

```python
# For "users" table:
def users_source(dynamic_where=None, dynamic_columns=None):
    # Engine detects: function accepts optimization parameters!
    # Engine will call: users_source(
    #     dynamic_where="users.id > 100",
    #     dynamic_columns=["id", "name"]
    # )
    ...
```

### Step 4: Source Uses Optimizations

```python
def users_source(dynamic_where=None, dynamic_columns=None):
    # Engine passes optimizations:
    # dynamic_where = "users.id > 100"
    # dynamic_columns = ["id", "name"]
    
    # Build optimized query
    columns = dynamic_columns or ["*"]  # ["id", "name"]
    where = dynamic_where or ""         # "users.id > 100"
    
    query = f"SELECT {', '.join(columns)} FROM users"
    if where:
        query += f" WHERE {where}"
    
    # Final query: "SELECT id, name FROM users WHERE users.id > 100"
    # Instead of: "SELECT * FROM users" (then filter in Python)
    
    return execute(query)
```

### Step 5: Results

**Without optimizations:**
- Fetches: All columns, all rows (1,000,000 rows × 10 columns)
- Filters: In Python (slow)
- Memory: High

**With optimizations:**
- Fetches: Only id, name columns, only rows where id > 100 (500 rows × 2 columns)
- Filters: In database (fast, uses index)
- Memory: Low

**Result: 1000x less data transferred, 10x faster!**

---

## "Keep Flag for Compatibility" Explained

### Current Situation (Has Flag)

```python
# Current code uses BOTH flag and protocol detection
if root_metadata.get('is_database_source') and (root_required_columns or pushable_where_sql):
    # Check function signature
    sig = inspect.signature(original_source_fn)
    if len(sig.parameters) > 0:
        # Apply optimizations
        ...
```

**Problem:** Flag is redundant - signature check already works!

### Migration Path

**Phase 1: Add Protocol Detection (Keep Flag)**

```python
# New code: Check protocol FIRST, fall back to flag
sig = inspect.signature(source_fn)
supports_protocol = 'dynamic_where' in sig.parameters or 'dynamic_columns' in sig.parameters

if supports_protocol:
    # Use protocol (new way)
    apply_optimizations()
elif root_metadata.get('is_database_source'):
    # Use flag (old way - for backward compatibility)
    apply_optimizations()
```

**Why keep flag?**
- ✅ Existing code still works
- ✅ Users can migrate gradually
- ✅ No breaking changes

**Phase 2: Remove Flag (Later)**

```python
# After users migrate, remove flag completely
if supports_protocol:
    apply_optimizations()
# No flag check - protocol is the only way
```

---

## Real-World Example: Database Source

### Current Implementation (Uses Flag)

```python
# db_connector.py
def create_table_source(pool, table_name, ...):
    def source_fn(dynamic_where=None, dynamic_columns=None):
        # Accepts protocol parameters
        ...
    return source_fn

# User code
engine.register(
    "users",
    create_table_source(pool, "users"),
    is_database_source=True  # ← Flag needed!
)
```

### Future Implementation (Protocol Only)

```python
# db_connector.py (same function)
def create_table_source(pool, table_name, ...):
    def source_fn(dynamic_where=None, dynamic_columns=None):
        # Accepts protocol parameters
        ...
    return source_fn

# User code
engine.register(
    "users",
    create_table_source(pool, "users")
    # No flag needed! Engine detects protocol automatically
)
```

**Engine automatically detects:**
- Function accepts `dynamic_where`? ✅ YES
- Function accepts `dynamic_columns`? ✅ YES
- → Apply optimizations!

---

## Summary

### Protocol Detection

**What:** Engine checks function signature to see if it accepts optimization parameters

**How:** Uses `inspect.signature()` to check for `dynamic_where` and `dynamic_columns` parameters

**Why:** Automatic detection - no flags needed!

### Optimizations

**Filter Pushdown (`dynamic_where`):**
- Pushes WHERE clause to source
- Source filters before sending data
- Less data transferred, faster

**Column Pruning (`dynamic_columns`):**
- Only fetches needed columns
- Source selects specific columns
- Less data transferred, less memory

### Migration

**Phase 1:** Add protocol detection, keep flag for compatibility
**Phase 2:** Remove flag, use protocol only

**Result:** Simpler API, same functionality, automatic detection!

