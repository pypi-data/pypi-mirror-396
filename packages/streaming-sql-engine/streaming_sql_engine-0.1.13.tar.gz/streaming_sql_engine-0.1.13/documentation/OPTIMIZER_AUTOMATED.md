# Optimizer is Fully Automated

## ✅ Yes, the Optimizer Runs Automatically!

The optimizer is **completely automated** - it runs for every query without any configuration needed.

## How It Works

### 1. Automatic Execution Flow

```
User calls: engine.query("SELECT ...")
    ↓
engine.py: parse_sql() → AST
    ↓
engine.py: build_logical_plan() → Logical Plan
    ↓
planner.py: AUTOMATICALLY calls optimizer:
    - analyze_required_columns() → Column pruning
    - analyze_filter_pushdown() → Filter pushdown
    ↓
executor.py: Uses optimizations automatically
```

### 2. Code Evidence

**In `planner.py` (lines 83-92):**

```python
# Build initial plan
plan = LogicalPlan(...)

# Apply optimizations (AUTOMATIC!)
from .optimizer import analyze_required_columns, analyze_filter_pushdown

# Analyze required columns (column pruning)
plan.required_columns = analyze_required_columns(plan)

# Analyze filter pushdown
pushable_where, remaining_where = analyze_filter_pushdown(plan)
plan.pushable_where_expr = pushable_where
plan.where_expr = remaining_where

return plan
```

**In `engine.py` (line 109):**

```python
# Build logical plan (optimizer runs automatically inside)
logical_plan = build_logical_plan(ast, self._sources.keys())
```

**In `executor.py` (lines 55-104):**

```python
# Uses optimizations automatically
root_required_columns = plan.required_columns.get(plan.root_table)
pushable_where_sql = expression_to_sql_string(plan.pushable_where_expr)

# Apply optimizations if protocol supported
if source_supports_optimizations(root_source_fn):
    return original_source_fn(
        dynamic_where=pushable_where_sql,
        dynamic_columns=list(root_required_columns)
    )
```

## What Optimizations Are Applied Automatically

### 1. Column Pruning (Automatic)

**What it does:**

- Analyzes SELECT, WHERE, and JOIN clauses
- Determines which columns are actually needed from each table
- Adds `required_columns` to the plan

**Example:**

```sql
SELECT users.name FROM users JOIN orders ON users.id = orders.user_id
```

**Optimizer automatically determines:**

- `users` needs: `name`, `id` (for join)
- `orders` needs: `user_id` (for join)

**Result:** Only these columns are requested from sources (if protocol supported)

### 2. Filter Pushdown (Automatic)

**What it does:**

- Analyzes WHERE clause
- Identifies conditions that only reference root table
- Splits into pushable vs non-pushable conditions

**Example:**

```sql
SELECT * FROM users JOIN orders ON users.id = orders.user_id
WHERE users.age > 30 AND orders.total > 100
```

**Optimizer automatically determines:**

- Pushable: `users.age > 30` (only references root table)
- Non-pushable: `orders.total > 100` (references joined table)

**Result:** `users.age > 30` is pushed to source (if protocol supported)

## Protocol Detection (Also Automatic)

**In `executor.py` (lines 80-88):**

```python
def source_supports_optimizations(source_fn):
    """Check if source implements optimization protocol."""
    try:
        sig = inspect.signature(source_fn)
        params = list(sig.parameters.keys())
        return 'dynamic_where' in params or 'dynamic_columns' in params
    except (ValueError, TypeError):
        return False
```

**What this means:**

- Engine automatically detects if source supports protocol
- If yes → optimizations are applied automatically
- If no → works normally, no optimizations

## Summary

✅ **Optimizer runs automatically** - No configuration needed
✅ **Column pruning is automatic** - Analyzes query to find needed columns
✅ **Filter pushdown is automatic** - Analyzes WHERE clause to find pushable conditions
✅ **Protocol detection is automatic** - Checks function signature automatically
✅ **Optimizations apply automatically** - If protocol supported, optimizations are used

## No Manual Configuration Needed!

**You don't need to:**

- ❌ Call optimizer manually
- ❌ Configure optimization settings
- ❌ Enable optimizations
- ❌ Set flags or parameters

**You just:**

- ✅ Write SQL query
- ✅ Register sources (with protocol if you want optimizations)
- ✅ Execute query
- ✅ Optimizations happen automatically!

## Example

```python
from streaming_sql_engine import Engine

engine = Engine()

# Register source with protocol (optimizations apply automatically!)
def my_source(dynamic_where=None, dynamic_columns=None):
    # Build query with optimizations
    query = build_query(dynamic_where, dynamic_columns)
    return execute_query(query)

engine.register("users", my_source)

# Query - optimizer runs automatically!
for row in engine.query("SELECT users.name FROM users WHERE users.age > 30"):
    print(row)

# What happens automatically:
# 1. Optimizer analyzes query
# 2. Determines: need "name" and "age" columns, WHERE clause pushable
# 3. Detects protocol (function accepts dynamic_where/dynamic_columns)
# 4. Calls: my_source(dynamic_where="users.age > 30", dynamic_columns=["name", "age"])
# 5. Source filters and selects only needed columns
# 6. Results returned
```

**Everything is automatic!** 🎉

