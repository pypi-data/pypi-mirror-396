# Why Protocol Parameters Are in Source Functions

## The Question

**Why do source functions need to accept `dynamic_where` and `dynamic_columns`?**
**Why can't the engine handle filtering/column selection internally?**

## Short Answer

**The engine DOES handle it internally**, but sources need to **accept** these parameters to enable **optimizations**. Without the protocol, the engine still works, but without optimizations.

---

## Two Approaches: With and Without Protocol

### Approach 1: Simple Source (No Protocol) - Engine Handles Everything

```python
def simple_source():
    """Simple source - no protocol."""
    # Fetch ALL data from source
    return execute("SELECT * FROM users")  # Gets 1,000,000 rows, all columns

# Engine handles filtering/selection AFTER getting data
engine.register("users", simple_source)

query = "SELECT users.name FROM users WHERE users.id > 100"

# What happens:
# 1. Source returns ALL 1,000,000 rows with ALL columns
# 2. Engine filters in Python: if row['id'] > 100
# 3. Engine selects columns: row['name']
# ✅ Works, but SLOW (processes 1M rows in Python)
```

**Result:** Works, but inefficient (processes all data in Python)

---

### Approach 2: Protocol Source - Source Handles Optimizations

```python
def optimized_source(dynamic_where=None, dynamic_columns=None):
    """Protocol source - optimizations enabled."""
    # Build query with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""

    query = f"SELECT {', '.join(columns)} FROM users"
    if where:
        query += f" WHERE {where}"

    # Source filters/selects BEFORE returning data
    return execute(query)  # Gets only 500 rows, only 'name' column

# Engine detects protocol and passes optimizations
engine.register("users", optimized_source)

query = "SELECT users.name FROM users WHERE users.id > 100"

# What happens:
# 1. Engine analyzes query → needs 'name', WHERE 'id > 100'
# 2. Engine detects protocol → function accepts dynamic_where/dynamic_columns
# 3. Engine calls: optimized_source(dynamic_where="users.id > 100", dynamic_columns=["id", "name"])
# 4. Source executes: "SELECT id, name FROM users WHERE users.id > 100"
# 5. Source returns only 500 rows, only needed columns
# ✅ Works AND FAST (source filters/selects efficiently)
```

**Result:** Works AND efficient (source filters/selects before sending data)

---

## Why This Architecture?

### The Problem: Different Sources Have Different Capabilities

**Database source:**

- Can filter efficiently (uses indexes)
- Can select specific columns (SQL)
- Should filter/select at database level

**API source:**

- Can filter via query parameters (`?active=true`)
- Can select fields via parameters (`?fields=name,email`)
- Should filter/select at API level

**File source:**

- Can filter while reading (skip rows)
- Can select columns while reading (skip columns)
- Should filter/select while reading

**Simple iterator:**

- Can't filter/select efficiently
- Engine must handle it

### The Solution: Protocol-Based Detection

**Engine automatically detects:**

- Does source accept `dynamic_where`? → Can push filters
- Does source accept `dynamic_columns`? → Can prune columns

**If yes:** Engine passes parameters → Source optimizes → Fast!
**If no:** Engine handles it internally → Works, but slower

---

## What the Engine Does Internally

### Step 1: Analyzes Query (Automatic)

```python
# In planner.py (automatic)
plan.required_columns = analyze_required_columns(plan)
plan.pushable_where_expr = analyze_filter_pushdown(plan)
```

**Engine determines:**

- Which columns are needed: `['id', 'name']`
- Which WHERE clauses can be pushed: `"users.id > 100"`

### Step 2: Detects Protocol (Automatic)

```python
# In executor.py (automatic)
def source_supports_optimizations(source_fn):
    sig = inspect.signature(source_fn)
    return 'dynamic_where' in params or 'dynamic_columns' in params
```

**Engine checks:** Does source accept these parameters?

### Step 3: Applies Optimizations (Automatic)

```python
# In executor.py (automatic)
if source_supports_optimizations(root_source_fn):
    # Engine passes optimization parameters
    return original_source_fn(
        dynamic_where="users.id > 100",
        dynamic_columns=['id', 'name']
    )
```

**Engine calls source with optimizations**

### Step 4: Source Uses Optimizations

```python
# In YOUR source function
def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Source receives optimization parameters from engine
    query = build_query(dynamic_where, dynamic_columns)
    return execute(query)  # Efficient!
```

**Source uses parameters to optimize**

---

## Why Not Handle Everything in Engine?

### Option A: Engine Handles Everything (Current for Simple Sources)

**Pros:**

- ✅ Simple sources work without modification
- ✅ No protocol needed

**Cons:**

- ❌ Inefficient (processes all data in Python)
- ❌ Can't use source-level optimizations (database indexes, API filters)

### Option B: Protocol-Based (Current for Optimized Sources)

**Pros:**

- ✅ Efficient (source filters/selects before sending)
- ✅ Uses source-level optimizations (database indexes, API filters)
- ✅ Less data transfer
- ✅ Less memory usage

**Cons:**

- ⚠️ Source needs to accept parameters (but simple - just add them!)

---

## The Key Insight

**The engine DOES handle it**, but:

1. **For simple sources:** Engine handles filtering/selection AFTER getting data (works, but slower)

2. **For protocol sources:** Engine PASSES optimization parameters, source handles filtering/selection BEFORE sending data (works AND faster)

**The protocol enables optimizations, but the engine still works without it!**

---

## Example: Both Approaches Work

### Simple Source (No Protocol)

```python
def simple_source():
    return iter([{"id": 1, "name": "Alice", "email": "..."}, ...])

engine.register("users", simple_source)

# Query works!
for row in engine.query("SELECT users.name FROM users WHERE users.id > 100"):
    print(row)
# ✅ Works - engine filters/selects in Python
```

### Protocol Source (With Optimizations)

```python
def optimized_source(dynamic_where=None, dynamic_columns=None):
    query = build_query(dynamic_where, dynamic_columns)
    return execute(query)

engine.register("users", optimized_source)

# Same query, but faster!
for row in engine.query("SELECT users.name FROM users WHERE users.id > 100"):
    print(row)
# ✅ Works AND faster - source filters/selects efficiently
```

---

## Summary

**Why protocol parameters are in source functions:**

1. **Engine analyzes query** → Determines optimizations needed
2. **Engine detects protocol** → Checks if source accepts parameters
3. **Engine passes parameters** → Calls source with optimizations
4. **Source uses parameters** → Filters/selects efficiently

**Without protocol:**

- ✅ Engine still works
- ✅ Engine handles filtering/selection internally
- ⚠️ Less efficient (processes all data in Python)

**With protocol:**

- ✅ Engine works
- ✅ Source handles filtering/selection efficiently
- ✅ Much faster (source optimizes before sending data)

**The protocol is optional but enables huge performance improvements!**


