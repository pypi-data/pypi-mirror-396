# Better Approach: Why Manual Parsing Exists and How to Improve It

## The Problem You Identified

**Why does the source function need manual `if` statements to parse the WHERE clause?**

```python
if dynamic_where:
    if "name = 'Electronics'" in dynamic_where:
        if row.get('name') != 'Electronics':
            continue
```

This is **inefficient and error-prone**!

## Why It Exists

### The Engine's Design

**Engine converts expression to SQL string:**

```python
# In executor.py
pushable_where_sql = expression_to_sql_string(plan.pushable_where_expr)
# Result: "products.price > 100" (string)

# Engine calls source with string
source_fn(dynamic_where="products.price > 100")
```

**Why string?** Because databases can use SQL strings directly:

```python
def db_source(dynamic_where=None):
    query = f"SELECT * FROM table WHERE {dynamic_where}"  # ✅ Works!
    return execute(query)
```

**But files can't execute SQL!** They need to parse and evaluate:

```python
def file_source(dynamic_where=None):
    # ❌ Can't execute SQL string
    # Need to parse and evaluate manually
    if "price > 100" in dynamic_where:
        # Manual parsing...
```

## Better Solution: Pass Expression AST Instead

**The engine already has the expression AST!** We could pass that instead of converting to string.

### Current Approach (String-Based)

```python
# Engine converts to string
pushable_where_sql = expression_to_sql_string(plan.pushable_where_expr)
source_fn(dynamic_where="products.price > 100")  # String

# File source needs to parse
if "price > 100" in dynamic_where:  # ❌ Manual parsing
    ...
```

### Better Approach (AST-Based)

```python
# Engine passes AST directly
source_fn(dynamic_where_expr=plan.pushable_where_expr)  # AST

# File source uses evaluator
from streaming_sql_engine.evaluator import evaluate_expression
if not evaluate_expression(dynamic_where_expr, row):  # ✅ No parsing!
    continue
```

## Why String Format Was Chosen

**Historical reason:**

1. Engine designed for databases first
2. Databases can execute SQL strings directly
3. File sources added later
4. String format kept for compatibility

**Current limitation:**

- File sources need manual parsing (inefficient)
- API sources need conversion to query parameters
- Only database sources benefit fully

## Recommended Solutions

### Solution 1: Don't Support Filter Pushdown for Files

**Simplest approach:**

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    # Ignore dynamic_where - let engine filter
    # Only support column pruning (which is easy)
    if dynamic_columns:
        # Column pruning
        ...
    # Engine will filter after getting data
```

**Pros:**

- ✅ Simple
- ✅ No parsing needed
- ✅ Still gets column pruning optimization

**Cons:**

- ❌ No filter pushdown for files

### Solution 2: Use Evaluator with Expression AST

**Better approach (requires protocol change):**

```python
# Change protocol to accept expression AST
def file_source(dynamic_where_expr=None, dynamic_columns=None):
    from streaming_sql_engine.evaluator import evaluate_expression

    for row in read_file():
        if dynamic_where_expr:  # AST, not string
            if not evaluate_expression(dynamic_where_expr, row):
                continue
        yield row
```

**Pros:**

- ✅ No parsing needed
- ✅ Robust (uses engine's evaluator)
- ✅ Works for all expression types

**Cons:**

- ⚠️ Requires protocol change

### Solution 3: Use SQL Parser (Current Workaround)

**For now, use a proper SQL parser:**

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    if dynamic_where:
        # Parse SQL string properly
        from sqlglot import parse_one
        expr = parse_one(f"SELECT * FROM dummy WHERE {dynamic_where}")
        where_expr = expr.args['where'].this

        # Use evaluator
        from streaming_sql_engine.evaluator import evaluate_expression
        if not evaluate_expression(where_expr, row):
            continue
```

**Pros:**

- ✅ Robust parsing
- ✅ Uses evaluator
- ✅ Works with current protocol

**Cons:**

- ⚠️ Extra parsing step (string → AST → evaluation)

## Summary

**Why manual parsing exists:**

- Engine passes SQL string (for database compatibility)
- File sources need to evaluate in Python
- Manual parsing is a workaround

**Better approaches:**

1. **Don't support filter pushdown for files** (simplest)
2. **Change protocol to pass AST** (best, but requires change)
3. **Parse SQL string properly** (current workaround)

**For your example:** The manual `if` statements are a **simplified workaround**. In production, you'd either:

- Use a proper SQL parser + evaluator
- Or skip filter pushdown for files (let engine filter)
