# How Protocol Detection Works - Step by Step

## The Question

**How does `register_file_source(engine, "categories", str(CSV_FILE))` work?**
**How does the engine know what to optimize?**

---

## Step-by-Step Flow

### Step 1: `register_file_source()` Creates Protocol Function

```python
register_file_source(engine, "categories", "data/categories.csv")
```

**What happens:**

1. `register_file_source()` calls `create_protocol_source("data/categories.csv")`
2. `create_protocol_source()` creates a function with protocol parameters:

```python
def csv_source(dynamic_where: Optional[str] = None,
              dynamic_columns: Optional[list] = None) -> Iterator[Dict]:
    # This function accepts protocol parameters!
    # Engine will detect this automatically
    ...
```

3. This function is registered with the engine:

```python
engine.register("categories", csv_source)
```

**Key Point:** The function **accepts** `dynamic_where` and `dynamic_columns` parameters.

---

### Step 2: Engine Detects Protocol (Automatic!)

When you execute a query:

```python
engine.query("SELECT categories.name FROM categories WHERE categories.id > 100")
```

**What happens in `executor.py`:**

```python
# Engine checks function signature using inspect.signature()
def source_supports_optimizations(source_fn):
    sig = inspect.signature(source_fn)
    params = list(sig.parameters.keys())

    # Check if function accepts protocol parameters
    return 'dynamic_where' in params or 'dynamic_columns' in params

# For csv_source:
# params = ['dynamic_where', 'dynamic_columns']
# 'dynamic_where' in params → True ✅
# 'dynamic_columns' in params → True ✅
# Result: Protocol detected!
```

**Key Point:** Engine uses Python's `inspect.signature()` to check function parameters automatically.

---

### Step 3: Engine Analyzes Query (Automatic!)

The engine analyzes your SQL query:

```sql
SELECT categories.name FROM categories WHERE categories.id > 100
```

**Engine determines:**

- **Required columns:** `['id', 'name']` (id needed for WHERE, name needed for SELECT)
- **Pushable WHERE clause:** `"categories.id > 100"` (can be pushed to source)

**Key Point:** Engine analyzes query automatically to determine optimizations.

---

### Step 4: Engine Passes Optimizations (Automatic!)

If protocol is detected, engine wraps the source function:

```python
# In executor.py
if source_supports_optimizations(root_source_fn):
    original_source_fn = root_source_fn  # csv_source

    def optimized_source_fn():
        # Call source with optimization parameters!
        return original_source_fn(
            dynamic_where="categories.id > 100",      # WHERE clause
            dynamic_columns=['id', 'name']           # Only needed columns
        )

    root_source_fn = optimized_source_fn
```

**Key Point:** Engine automatically passes optimization parameters to your source function.

---

### Step 5: Source Function Uses Optimizations

The `csv_source` function receives the parameters:

```python
def csv_source(dynamic_where: Optional[str] = None,
              dynamic_columns: Optional[list] = None):
    # dynamic_where = "categories.id > 100"
    # dynamic_columns = ['id', 'name']

    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply filter pushdown
            if dynamic_where:
                # Parse and evaluate WHERE clause
                if not evaluate_expression(where_expr, row):
                    continue  # Skip row

            # Apply column pruning
            if dynamic_columns:
                row = {k: v for k, v in row.items() if k in dynamic_columns}

            yield row
```

**Key Point:** Source function uses the parameters to filter and prune columns.

---

## Visual Flow Diagram

```
User Code:
  register_file_source(engine, "categories", "data.csv")

  ↓

Helper Function:
  Creates csv_source(dynamic_where=None, dynamic_columns=None)

  ↓

Engine Registration:
  engine.register("categories", csv_source)

  ↓

Query Execution:
  engine.query("SELECT name FROM categories WHERE id > 100")

  ↓

Protocol Detection:
  inspect.signature(csv_source)
  → Finds: ['dynamic_where', 'dynamic_columns']
  → Protocol detected! ✅

  ↓

Query Analysis:
  Required columns: ['id', 'name']
  WHERE clause: "categories.id > 100"

  ↓

Optimization Application:
  csv_source(
    dynamic_where="categories.id > 100",
    dynamic_columns=['id', 'name']
  )

  ↓

Source Execution:
  - Reads CSV file
  - Filters rows (id > 100)
  - Prunes columns (only id, name)
  - Yields optimized rows
```

---

## Key Points

### 1. **Protocol Detection is Automatic**

The engine **automatically** checks if your function accepts `dynamic_where` or `dynamic_columns`:

```python
# Engine code (automatic)
sig = inspect.signature(source_fn)
params = list(sig.parameters.keys())
has_protocol = 'dynamic_where' in params or 'dynamic_columns' in params
```

**You don't need to do anything!** Just make sure your function accepts these parameters.

---

### 2. **Helper Functions Create Protocol Functions**

`register_file_source()` creates a function that **already has** protocol parameters:

```python
# What register_file_source() does internally
def csv_source(dynamic_where=None, dynamic_columns=None):
    # Protocol parameters already here!
    ...
```

**You don't need to add them manually!** The helper does it for you.

---

### 3. **Engine Passes Optimizations Automatically**

When protocol is detected, engine **automatically** passes:

- `dynamic_where`: SQL WHERE clause string (e.g., `"categories.id > 100"`)
- `dynamic_columns`: List of needed columns (e.g., `['id', 'name']`)

**You don't need to extract them from the query!** The engine does it automatically.

---

### 4. **Source Function Uses Optimizations**

Your source function receives the parameters and uses them:

```python
def csv_source(dynamic_where=None, dynamic_columns=None):
    # Use dynamic_where to filter rows
    if dynamic_where:
        # Filter logic
        ...

    # Use dynamic_columns to prune columns
    if dynamic_columns:
        # Column pruning logic
        ...
```

**The helper functions handle this automatically!** You don't need to implement it.

---

## Summary

**How `register_file_source()` works:**

1. ✅ Creates function with `dynamic_where` and `dynamic_columns` parameters
2. ✅ Registers function with engine
3. ✅ Engine detects protocol automatically (via `inspect.signature()`)
4. ✅ Engine analyzes query automatically (determines optimizations)
5. ✅ Engine passes optimizations automatically (WHERE clause + columns)
6. ✅ Source function uses optimizations automatically (filter + prune)

**Everything is automatic!** You just call `register_file_source()` and it works! 🎉

---

## Comparison: Manual vs Helper

### Manual Way (Before)

```python
# You need to:
# 1. Create function with protocol parameters
# 2. Parse WHERE clause manually
# 3. Use evaluator manually
# 4. Handle column pruning manually
# ... 50+ lines of code ...

def csv_source(dynamic_where=None, dynamic_columns=None):
    # Manual SQL parsing
    # Manual filter evaluation
    # Manual column pruning
    ...
```

### Helper Way (Now)

```python
# Just one line!
register_file_source(engine, "categories", "data.csv")

# Everything is automatic:
# ✅ Protocol parameters added automatically
# ✅ SQL parsing handled automatically
# ✅ Filter evaluation handled automatically
# ✅ Column pruning handled automatically
```

**That's the magic!** The helper functions do all the work for you.


