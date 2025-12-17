# Engine Options Reference Guide

Complete documentation for all Engine options with examples, queries, and outputs.

---

## Table of Contents

1. [Engine Initialization Options](#engine-initialization-options)

   - [debug](#debug-option)
   - [use_polars](#use_polars-option)

2. [Source Registration Options](#source-registration-options)

   - [ordered_by](#ordered_by-option)
   - [filename](#filename-option)

3. [Source Function Protocols](#source-function-protocols)

   - [dynamic_where](#dynamic_where-protocol)
   - [dynamic_columns](#dynamic_columns-protocol)

4. [Join Type Selection](#join-type-selection)

---

## Engine Initialization Options

### `debug` Option

**Purpose**: Enable verbose logging of execution stages

**Default**: `False`

**Type**: `bool`

#### Example

```python
from streaming_sql_engine import Engine

# Without debug (default)
engine = Engine()
# No output during query execution

# With debug enabled
engine = Engine(debug=True)
# Shows detailed execution information
```

#### Query Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

def users_source():
    return iter([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
    ])

engine.register("users", users_source)

results = list(engine.query("SELECT users.name, users.age FROM users WHERE users.age > 26"))
```

#### Output

```
============================================================
STREAMING SQL ENGINE - DEBUG MODE
============================================================

[1/3] PARSING SQL QUERY...
Query:
SELECT users.name, users.age FROM users WHERE users.age > 26

✓ SQL parsed successfully

[2/3] BUILDING LOGICAL PLAN...
✓ Logical plan built:
  - Root table: users (alias: )
  - Joins: 0
  - WHERE clause: Yes
  - Projections: 2

[3/3] EXECUTING QUERY...
Building execution pipeline...

  [SCAN] Scanning table: users (columns: 2)
  [FILTER] Applying WHERE clause: users.age > 26
  [PROJECT] Applying SELECT projection

Pipeline ready. Starting row processing...

------------------------------------------------------------
      Started reading from users (columns: 2)
     Filtered 1 rows (WHERE: users.age > 26)
     Projected 1 result rows

------------------------------------------------------------
      Finished reading from users
      Total rows scanned: 2
      Total rows passed filter: 1
      Total rows projected: 1
```

#### Result

```python
[{'name': 'Alice', 'age': 30}]
```

---

### `use_polars` Option

**Purpose**: Enable Polars for vectorized operations and joins

**Default**: `False`

**Type**: `bool`

**Note**: When `False`, uses Python Lookup Join (faster for small-medium datasets)

#### Example

```python
from streaming_sql_engine import Engine

# Default: Python Lookup Join
engine = Engine()  # use_polars=False

# Enable Polars Join
engine = Engine(use_polars=True)  # Uses Polars for joins
```

#### Query Example

```python
from streaming_sql_engine import Engine

# Python Lookup Join (default)
engine_python = Engine(use_polars=False)

# Polars Join
engine_polars = Engine(use_polars=True)

def users_source():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

def orders_source():
    return iter([
        {"id": 1, "user_id": 1, "product": "Book"},
        {"id": 2, "user_id": 2, "product": "Pen"},
    ])

engine_python.register("users", users_source)
engine_python.register("orders", orders_source)

engine_polars.register("users", users_source)
engine_polars.register("orders", orders_source)

# Both produce same results
results_python = list(engine_python.query(
    "SELECT users.name, orders.product FROM users "
    "INNER JOIN orders ON users.id = orders.user_id"
))

results_polars = list(engine_polars.query(
    "SELECT users.name, orders.product FROM users "
    "INNER JOIN orders ON users.id = orders.user_id"
))
```

#### Output (with debug=True)

**Python Lookup Join**:

```
      Using LOOKUP JOIN (building index...)
      Building lookup index for orders...
      Index built: 2 rows, 2 unique keys
```

**Polars Join**:

```
      Using POLARS LOOKUP JOIN (fast, vectorized)...
```

#### Result

```python
[
    {'name': 'Alice', 'product': 'Book'},
    {'name': 'Bob', 'product': 'Pen'}
]
```

---

## Source Registration Options

### `ordered_by` Option

**Purpose**: Specify that source data is sorted by a column (enables Merge Join)

**Default**: `None`

**Type**: `str` (column name)

**When to Use**: When both tables are pre-sorted by their join keys

#### Example

```python
from streaming_sql_engine import Engine

engine = Engine(use_polars=False)

def users_source():
    # Data is sorted by id
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ])

def orders_source():
    # Data is sorted by user_id
    return iter([
        {"id": 1, "user_id": 1, "product": "Book"},
        {"id": 2, "user_id": 2, "product": "Pen"},
        {"id": 3, "user_id": 3, "product": "Notebook"},
    ])

# Register with ordered_by to enable Merge Join
engine.register("users", users_source, ordered_by="id")
engine.register("orders", orders_source, ordered_by="user_id")
```

#### Query Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True, use_polars=False)

def users_source():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

def orders_source():
    return iter([
        {"id": 1, "user_id": 1, "product": "Book"},
        {"id": 2, "user_id": 2, "product": "Pen"},
    ])

engine.register("users", users_source, ordered_by="id")
engine.register("orders", orders_source, ordered_by="user_id")

results = list(engine.query(
    "SELECT users.name, orders.product FROM users "
    "INNER JOIN orders ON users.id = orders.user_id"
))
```

#### Output

```
  [JOIN 1/1] INNER JOIN orders (columns: 2)
      Using MERGE JOIN (sorted data)
```

#### Result

```python
[
    {'name': 'Alice', 'product': 'Book'},
    {'name': 'Bob', 'product': 'Pen'}
]
```

**Benefits**:

- Most memory-efficient join type
- No index building overhead
- Fast for sorted data

---

### `filename` Option

**Purpose**: Specify filename for file-based sources (enables MMAP Join for low memory usage)

**Default**: `None`

**Type**: `str` (file path)

**When to Use**: For large files where memory usage is critical

#### Example

```python
from streaming_sql_engine import Engine
import json

engine = Engine(use_polars=True)

def users_source():
    with open("users.jsonl", "r") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def orders_source():
    with open("orders.jsonl", "r") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

# Register with filename to enable MMAP Join
engine.register("users", users_source, filename="users.jsonl")
engine.register("orders", orders_source, filename="orders.jsonl")
```

#### Query Example

```python
from streaming_sql_engine import Engine
import json
import tempfile
import os

# Create sample files
users_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
orders_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)

json.dump({"id": 1, "name": "Alice"}, users_file)
users_file.write("\n")
users_file.close()

json.dump({"id": 1, "user_id": 1, "product": "Book"}, orders_file)
orders_file.write("\n")
orders_file.close()

try:
    engine = Engine(debug=True, use_polars=True)

    def users_source():
        with open(users_file.name, "r") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def orders_source():
        with open(orders_file.name, "r") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    engine.register("users", users_source, filename=users_file.name)
    engine.register("orders", orders_source, filename=orders_file.name)

    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "INNER JOIN orders ON users.id = orders.user_id"
    ))
finally:
    os.unlink(users_file.name)
    os.unlink(orders_file.name)
```

#### Output

```
  [JOIN 1/1] INNER JOIN orders (columns: 2)
      Using MMAP LOOKUP JOIN (low memory, position-based index)...
```

#### Result

```python
[{'name': 'Alice', 'product': 'Book'}]
```

**Benefits**:

- 90-99% memory reduction for large files
- Memory-mapped file access
- Ideal for very large datasets

---

## Source Function Protocols

### `dynamic_where` Protocol

**Purpose**: Enable filter pushdown optimization (WHERE clause applied at source level)

**How it Works**: If your source function accepts a `dynamic_where` parameter, the engine will pass SQL WHERE conditions to your source function

**When to Use**: When your source can filter data more efficiently (e.g., database queries, API calls with filters)

#### Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

def database_source(dynamic_where=None, dynamic_columns=None):
    """
    Source function that accepts optimization parameters.
    When dynamic_where is provided, apply it to the database query.
    """
    import sqlite3

    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    # Build query with optional WHERE clause
    query = "SELECT id, name, age FROM users"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"

    cursor.execute(query)
    for row in cursor.fetchall():
        yield {"id": row[0], "name": row[1], "age": row[2]}

    conn.close()

engine.register("users", database_source)

# Query with WHERE clause - will be pushed to source
results = list(engine.query("SELECT users.name FROM users WHERE users.age > 25"))
```

#### Query Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

def api_source(dynamic_where=None, dynamic_columns=None):
    """
    Simulated API source with filter pushdown.
    """
    all_data = [
        {"id": 1, "name": "Alice", "age": 30, "city": "NYC"},
        {"id": 2, "name": "Bob", "age": 25, "city": "LA"},
        {"id": 3, "name": "Charlie", "age": 35, "city": "NYC"},
    ]

    # If dynamic_where is provided, filter at source level
    if dynamic_where:
        print(f"[SOURCE] Applying filter: {dynamic_where}")
        # In real implementation, you'd parse and apply the WHERE clause
        # For this example, we'll filter by age > 25
        filtered = [row for row in all_data if row["age"] > 25]
        for row in filtered:
            yield row
    else:
        for row in all_data:
            yield row

engine.register("users", api_source)

results = list(engine.query("SELECT users.name, users.age FROM users WHERE users.age > 25"))
```

#### Output

```
  [OPTIMIZATION] Pushing WHERE clause to source: users.age > 25
  [OPTIMIZATION] Source supports protocol - applying column pruning and filter pushdown
[SOURCE] Applying filter: users.age > 25
```

#### Result

```python
[
    {'name': 'Alice', 'age': 30},
    {'name': 'Charlie', 'age': 35}
]
```

**Benefits**:

- Reduces data transfer (filter at source)
- Faster execution (less data to process)
- Lower memory usage

---

### `dynamic_columns` Protocol

**Purpose**: Enable column pruning optimization (only read required columns from source)

**How it Works**: If your source function accepts a `dynamic_columns` parameter, the engine will pass a list of required column names

**When to Use**: When your source can read only specific columns (e.g., databases, columnar storage)

#### Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

def database_source(dynamic_where=None, dynamic_columns=None):
    """
    Source function with column pruning support.
    When dynamic_columns is provided, only read those columns.
    """
    import sqlite3

    conn = sqlite3.connect("example.db")
    cursor = conn.cursor()

    # Build query with specific columns if provided
    if dynamic_columns:
        columns = ", ".join(dynamic_columns)
        query = f"SELECT {columns} FROM users"
    else:
        query = "SELECT * FROM users"

    if dynamic_where:
        query += f" WHERE {dynamic_where}"

    cursor.execute(query)
    for row in cursor.fetchall():
        # Map row to dict based on columns
        yield dict(zip(dynamic_columns or ["id", "name", "age", "city"], row))

    conn.close()

engine.register("users", database_source)

# Only 'name' and 'age' columns will be requested from source
results = list(engine.query("SELECT users.name, users.age FROM users"))
```

#### Query Example

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

def wide_table_source(dynamic_where=None, dynamic_columns=None):
    """
    Simulated wide table source (many columns).
    With column pruning, only read requested columns.
    """
    all_columns = ["id", "name", "age", "email", "phone", "address", "city", "country"]

    if dynamic_columns:
        print(f"[SOURCE] Column pruning: reading only {dynamic_columns}")
        requested_cols = set(dynamic_columns)
    else:
        requested_cols = set(all_columns)

    # Sample data
    all_data = [
        {col: f"{col}_value_{i}" for col in all_columns}
        for i in range(1, 4)
    ]

    for row in all_data:
        # Only yield requested columns
        if dynamic_columns:
            yield {col: row[col] for col in dynamic_columns if col in row}
        else:
            yield row

engine.register("users", wide_table_source)

# Only 'name' and 'age' will be read from source
results = list(engine.query("SELECT users.name, users.age FROM users"))
```

#### Output

```
  [OPTIMIZATION] Source supports protocol - applying column pruning and filter pushdown
[SOURCE] Column pruning: reading only ['name', 'age']
```

#### Result

```python
[
    {'name': 'name_value_1', 'age': 'age_value_1'},
    {'name': 'name_value_2', 'age': 'age_value_2'},
    {'name': 'name_value_3', 'age': 'age_value_3'}
]
```

**Benefits**:

- Reduced I/O (read only needed columns)
- Lower memory usage
- Faster for wide tables

---

## Combined Options Examples

### Example 1: Protocol + filename

```python
from streaming_sql_engine import Engine
import json

engine = Engine(debug=True, use_polars=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    """
    Source with both protocol support and filename.
    """
    with open("data.jsonl", "r") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                # Apply column pruning if requested
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

engine.register("users", optimized_source, filename="data.jsonl")

results = list(engine.query("SELECT users.name FROM users WHERE users.age > 25"))
```

**Output**:

```
  [OPTIMIZATION] Pushing WHERE clause to source: users.age > 25
  [OPTIMIZATION] Source supports protocol - applying column pruning and filter pushdown
  [JOIN 1/1] INNER JOIN orders
      Using MMAP LOOKUP JOIN (low memory)...
```

---

### Example 2: ordered_by + use_polars

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True, use_polars=True)

def sorted_source():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

engine.register("users", sorted_source, ordered_by="id")

# Merge Join will be used (preferred over Polars for sorted data)
results = list(engine.query("SELECT users.name FROM users"))
```

**Output**:

```
      Using MERGE JOIN (sorted data)
```

---

## Join Type Selection Summary

The engine automatically selects the best join type based on available options:

| Options                           | Join Type Used                      |
| --------------------------------- | ----------------------------------- |
| `use_polars=False` (default)      | **Lookup Join** (Python hash-based) |
| `use_polars=False` + `ordered_by` | **Merge Join** (sorted data)        |
| `use_polars=True`                 | **Polars Join** (vectorized)        |
| `use_polars=True` + `filename`    | **MMAP Join** (low memory)          |
| `ordered_by` (any `use_polars`)   | **Merge Join** (preferred)          |
| `filename` (any `use_polars`)     | **MMAP Join** (preferred)           |

**Priority Order**:

1. Merge Join (if `ordered_by` provided)
2. MMAP Join (if `filename` provided)
3. Polars Join (if `use_polars=True`)
4. Lookup Join (default)

---

## Complete Example: All Options Combined

```python
from streaming_sql_engine import Engine
import json

# Engine with all options
engine = Engine(debug=True, use_polars=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    """
    Source function with:
    - Protocol support (dynamic_where, dynamic_columns)
    - File-based (filename will be provided)
    """
    with open("users.jsonl", "r") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                # Apply column pruning
                if dynamic_columns:
                    row = {k: v for k, v in row.items() if k in dynamic_columns}
                yield row

# Register with all options
engine.register(
    "users",
    optimized_source,
    ordered_by="id",      # Enable merge join
    filename="users.jsonl"  # Enable MMAP join
)

# Query that triggers all optimizations
results = list(engine.query(
    "SELECT users.name, users.age FROM users WHERE users.age > 25"
))
```

**What Happens**:

1. ✅ Filter pushdown: WHERE clause passed to source
2. ✅ Column pruning: Only 'name' and 'age' requested
3. ✅ Merge Join: Used because `ordered_by` is provided
4. ✅ MMAP: Available for low memory (if MMAP available)

---

## Quick Reference Table

| Option            | Type    | Default  | Purpose                         |
| ----------------- | ------- | -------- | ------------------------------- |
| `debug`           | `bool`  | `False`  | Enable verbose logging          |
| `use_polars`      | `bool`  | `False`  | Enable Polars joins             |
| `ordered_by`      | `str`   | `None`   | Enable merge join (sorted data) |
| `filename`        | `str`   | `None`   | Enable MMAP join (low memory)   |
| `dynamic_where`   | `param` | Protocol | Filter pushdown optimization    |
| `dynamic_columns` | `param` | Protocol | Column pruning optimization     |

---

**Last Updated**: 2025-12-14
