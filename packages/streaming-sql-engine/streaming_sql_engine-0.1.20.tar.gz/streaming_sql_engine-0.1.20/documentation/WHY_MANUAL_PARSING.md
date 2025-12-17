# Why Manual WHERE Clause Parsing in Source Functions?

## The Problem

You're right to question this! The manual parsing like:

```python
if dynamic_where:
    if "name = 'Electronics'" in dynamic_where:
        if row.get('name') != 'Electronics':
            continue
```

This is **inefficient and error-prone**. Why does the source need to parse a SQL string?

## The Answer: Different Sources Need Different Formats

The engine converts the WHERE expression to a **SQL string** because different sources need different formats:

### 1. **Database Sources** - Can Use SQL Directly ✅

```python
def db_source(dynamic_where=None, dynamic_columns=None):
    query = f"SELECT * FROM table"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"  # ✅ Can use SQL string directly!
    return execute(query)
```

**No parsing needed** - database understands SQL!

### 2. **API Sources** - Need Query Parameters

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        # Convert SQL to API query parameters
        if "active = true" in dynamic_where:
            params['active'] = 'true'
    # ✅ Converts to API format
```

**Some parsing needed** - but simpler (just extract values)

### 3. **File Sources** - Need Python Evaluation ❌

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    for row in read_file():
        if dynamic_where:
            # ❌ Need to parse SQL string and evaluate
            if "name = 'Electronics'" in dynamic_where:
                if row['name'] != 'Electronics':
                    continue
```

**Manual parsing** - inefficient and error-prone!

---

## Better Solution: Use Expression AST Instead of String

**The engine already has the expression AST!** We could pass that instead:

### Current (String-Based)

```python
# Engine converts to string
pushable_where_sql = expression_to_sql_string(plan.pushable_where_expr)
# Result: "products.price > 100"

# Source needs to parse string
if "price > 100" in dynamic_where:
    # Manual parsing...
```

### Better (AST-Based)

```python
# Engine passes AST directly
pushable_where_expr = plan.pushable_where_expr
# Result: exp.GT(exp.Column("price"), exp.Literal(100))

# Source uses evaluator
from streaming_sql_engine.evaluator import evaluate_expression
if evaluate_expression(pushable_where_expr, row):
    # ✅ No parsing needed!
```

---

## Why String Format Exists

**Historical reason:** The engine was designed for database sources first, which can use SQL strings directly. File sources came later and need parsing.

**Current limitation:** File sources need to parse SQL strings manually, which is inefficient.

---

## Recommended Approach for File Sources

### Option 1: Use Evaluator (Better)

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    # If engine passed AST, use evaluator
    from streaming_sql_engine.evaluator import evaluate_expression

    for row in read_file():
        if dynamic_where_expr:  # AST, not string
            if not evaluate_expression(dynamic_where_expr, row):
                continue
        yield row
```

**Problem:** Engine currently passes string, not AST.

### Option 2: Parse String Properly (Current Workaround)

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    # Parse SQL string properly (not manual if statements)
    if dynamic_where:
        # Use a proper SQL parser or evaluator
        # For now, manual parsing is a workaround
        ...
```

**Current approach:** Manual parsing (inefficient but works)

### Option 3: Don't Support Filter Pushdown for Files (Simplest)

```python
def file_source(dynamic_where=None, dynamic_columns=None):
    # Ignore dynamic_where - let engine filter
    # Only support column pruning
    if dynamic_columns:
        # Column pruning is easy
        ...
```

**Simplest:** Let engine handle filtering for files.

---

## The Real Answer

**For databases:** SQL string is perfect - no parsing needed ✅
**For APIs:** Some parsing needed - convert to query parameters ✅
**For files:** Manual parsing is inefficient - better to use evaluator with AST ⚠️

**The manual `if` statements are a workaround** because:

1. Engine passes SQL string (designed for databases)
2. Files can't execute SQL directly
3. Need to parse string to evaluate in Python
4. Manual parsing is quick but not robust

**Better solution:** Engine could pass expression AST, and sources use evaluator. But that requires changing the protocol.

---

## Summary

**Why manual parsing exists:**

- Engine passes SQL string (for database compatibility)
- File sources need to evaluate in Python
- Manual parsing is a workaround

**Better approach:**

- Engine could pass expression AST
- Sources use evaluator (no parsing needed)
- But requires protocol change

**For now:**

- Database sources: Use SQL string directly ✅
- File sources: Manual parsing (workaround) ⚠️
- Or: Don't support filter pushdown for files (let engine filter)


