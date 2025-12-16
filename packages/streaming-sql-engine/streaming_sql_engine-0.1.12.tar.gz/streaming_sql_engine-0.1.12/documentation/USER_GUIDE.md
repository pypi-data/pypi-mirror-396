# User Guide: Streaming SQL Engine

A comprehensive guide for developers who want to use the Streaming SQL Engine library in their projects.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Core Concepts](#core-concepts)
4. [Basic Usage](#basic-usage)
5. [Registering Data Sources](#registering-data-sources)
6. [Writing SQL Queries](#writing-sql-queries)
7. [Supported SQL Features](#supported-sql-features)
8. [Advanced Features](#advanced-features)
9. [Common Patterns](#common-patterns)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)
12. [Examples](#examples)

---

## Introduction

The **Streaming SQL Engine** is a Python library that lets you execute SQL queries with joins across different data sources. Unlike traditional databases, you can join data from:

- **Databases** (MySQL, PostgreSQL)
- **REST APIs** (any HTTP API)
- **Files** (CSV, JSONL, JSON)
- **Any Python iterable** (generators, lists, etc.)

All using standard SQL syntax, with zero infrastructure setup.

### Key Benefits

- ✅ **Cross-system joins**: Join MySQL + PostgreSQL + API in one query
- ✅ **Streaming**: Processes row-by-row, memory efficient
- ✅ **Python-native**: Easy integration with Python applications
- ✅ **Zero-config**: Just `pip install` and use

---

## Installation

### Install from PyPI

```bash
pip install streaming-sql-engine
```

### Install from Source

```bash
git clone https://github.com/Ierofantis/streaming-sql-engine.git
cd streaming-sql-engine
pip install -e .
```

### Install Dependencies Only

```bash
pip install -r requirements.txt
```

**Required dependencies:**

- `sqlglot>=23.0.0` - SQL parsing
- `psycopg2-binary>=2.9.0` - PostgreSQL support
- `pymysql>=1.0.0` - MySQL support
- `DBUtils>=3.0.0` - Connection pooling
- `requests>=2.28.0` - HTTP API support
- `python-dotenv>=1.0.0` - Environment variables

---

## Core Concepts

### 1. **Engine**

The `Engine` class is the main interface. It manages registered data sources and executes SQL queries.

```python
from streaming_sql_engine import Engine

engine = Engine()
```

**Engine Modes:**

```python
# Debug mode: Shows detailed execution information
engine = Engine(debug=True)

# JSONL mode: Uses JSONL-based execution (simpler, lower CPU)
engine = Engine(use_jsonl_mode=True)
```

### 2. **Data Sources**

A **data source** is a Python function that returns an iterator of dictionaries. Each dictionary represents a row.

```python
def my_source():
    """A data source function."""
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])
```

**Key Requirements:**

- Must be a callable (function or lambda)
- Must return an iterator (or generator)
- Each item must be a dictionary
- Dictionary keys become column names

### 3. **Table Registration**

Before querying, you **register** data sources with table names:

```python
engine.register("users", my_source)
```

Now you can use `users` in SQL queries:

```sql
SELECT * FROM users
```

### 4. **Query Execution**

Execute SQL queries and get results as a generator:

```python
for row in engine.query("SELECT * FROM users"):
    print(row)
# Output: {'id': 1, 'name': 'Alice'}
#         {'id': 2, 'name': 'Bob'}
```

---

## Basic Usage

### Minimal Example

```python
from streaming_sql_engine import Engine

# 1. Create engine
engine = Engine()

# 2. Define data source
def users():
    return iter([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
    ])

# 3. Register source
engine.register("users", users)

# 4. Execute query
for row in engine.query("SELECT name, age FROM users WHERE age > 25"):
    print(row)
# Output: {'name': 'Alice', 'age': 30}
```

### With Joins

```python
from streaming_sql_engine import Engine

engine = Engine()

# Define sources
def users():
    return iter([
        {"id": 1, "name": "Alice", "dept_id": 10},
        {"id": 2, "name": "Bob", "dept_id": 20},
    ])

def departments():
    return iter([
        {"id": 10, "name": "Engineering"},
        {"id": 20, "name": "Sales"},
    ])

# Register sources
engine.register("users", users)
engine.register("departments", departments)

# Join query
query = """
    SELECT users.name, departments.name AS dept_name
    FROM users
    JOIN departments ON users.dept_id = departments.id
"""

for row in engine.query(query):
    print(row)
# Output: {'name': 'Alice', 'dept_name': 'Engineering'}
#         {'name': 'Bob', 'dept_name': 'Sales'}
```

---

## Registering Data Sources

### 1. **Simple Function**

```python
def products():
    return iter([
        {"id": 1, "name": "Widget", "price": 10.99},
        {"id": 2, "name": "Gadget", "price": 19.99},
    ])

engine.register("products", products)
```

### 2. **Lambda Function**

```python
engine.register("products", lambda: iter([
    {"id": 1, "name": "Widget"},
    {"id": 2, "name": "Gadget"},
]))
```

### 3. **Generator Function**

```python
def large_dataset():
    """Generate data on-the-fly."""
    for i in range(1, 1000000):
        yield {"id": i, "value": i * 2}

engine.register("large_table", large_dataset)
```

### 4. **From CSV File**

```python
import csv

def csv_source(filepath):
    """Read CSV file."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

engine.register("products", lambda: csv_source("products.csv"))
```

### 5. **From JSONL File**

```python
import json

def jsonl_source(filepath):
    """Read JSONL file."""
    with open(filepath, 'r') as f:
        for line in f:
            yield json.loads(line)

engine.register("products", lambda: jsonl_source("products.jsonl"))
```

### 6. **From REST API**

```python
import requests

def api_source():
    """Fetch data from REST API."""
    response = requests.get("https://api.example.com/products")
    for item in response.json():
        yield item

engine.register("products", api_source)
```

### 7. **From Database (PostgreSQL)**

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
from dotenv import load_dotenv

load_dotenv()

pool = create_pool_from_env()
engine = Engine()

# Register table from PostgreSQL
engine.register(
    "users",
    create_table_source(pool, "users", where_clause="active = true")
)
```

### 8. **From Database (MySQL)**

```python
from streaming_sql_engine import Engine, create_mysql_pool_from_env, create_table_source

pool = create_mysql_pool_from_env()
engine = Engine()

engine.register(
    "products",
    create_table_source(pool, "products", order_by="id")
)
```

### 9. **With Python Processing**

```python
def enriched_source():
    """Apply Python logic to data."""
    raw_data = fetch_from_api()
    for item in raw_data:
        # Add computed fields
        item['score'] = calculate_score(item)
        item['category'] = classify(item)
        yield item

engine.register("enriched_data", enriched_source)
```

### 10. **Ordered Sources (for Merge Joins)**

```python
# If your source is sorted by a column, register it for optimization
engine.register(
    "users",
    users_source,
    ordered_by="id"  # Enables merge join optimization
)
```

---

## Writing SQL Queries

### Basic SELECT

```python
# Select all columns
query = "SELECT * FROM users"

# Select specific columns
query = "SELECT name, email FROM users"

# Select with aliases
query = "SELECT name AS user_name, email AS user_email FROM users"
```

### FROM Clause

```python
# Single table
query = "SELECT * FROM users"

# With table alias
query = "SELECT u.name FROM users AS u"
```

### WHERE Clause

```python
# Comparison operators
query = "SELECT * FROM users WHERE age > 25"
query = "SELECT * FROM users WHERE age >= 18"
query = "SELECT * FROM users WHERE name = 'Alice'"
query = "SELECT * FROM users WHERE name != 'Bob'"

# Boolean operators
query = "SELECT * FROM users WHERE age > 25 AND active = true"
query = "SELECT * FROM users WHERE age < 18 OR age > 65"
query = "SELECT * FROM users WHERE NOT deleted"

# NULL checks
query = "SELECT * FROM users WHERE email IS NULL"
query = "SELECT * FROM users WHERE email IS NOT NULL"

# IN clause
query = "SELECT * FROM users WHERE id IN (1, 2, 3)"
query = "SELECT * FROM users WHERE status IN ('active', 'pending')"

# Table-qualified columns
query = "SELECT * FROM users WHERE users.age > 25"
```

### JOIN Clause

```python
# INNER JOIN
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
"""

# LEFT JOIN
query = """
    SELECT users.name, orders.total
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
"""

# Multiple JOINs
query = """
    SELECT users.name, orders.total, products.name AS product_name
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN products ON orders.product_id = products.id
"""

# With table aliases
query = """
    SELECT u.name, o.total
    FROM users AS u
    JOIN orders AS o ON u.id = o.user_id
"""
```

**Important:** Only **equality joins** are supported (`ON left.key = right.key`).

### Column Selection

```python
# Select specific columns
query = "SELECT name, email FROM users"

# Select with aliases
query = "SELECT name AS user_name FROM users"

# Select table-qualified columns
query = "SELECT users.name, orders.total FROM users JOIN orders ..."

# Select all columns from specific table
query = "SELECT users.*, orders.total FROM users JOIN orders ..."
```

---

## Supported SQL Features

### ✅ Supported Features

| Feature                     | Example                                   | Notes                    |
| --------------------------- | ----------------------------------------- | ------------------------ |
| **SELECT**                  | `SELECT col1, col2`                       | Column selection         |
| **Aliases**                 | `SELECT col AS alias`                     | Column and table aliases |
| **FROM**                    | `FROM table`                              | Single table             |
| **Table aliases**           | `FROM table AS t`                         | Table aliasing           |
| **INNER JOIN**              | `JOIN table ON left.key = right.key`      | Equality joins only      |
| **LEFT JOIN**               | `LEFT JOIN table ON left.key = right.key` | Equality joins only      |
| **WHERE**                   | `WHERE col > 100`                         | Filtering                |
| **Comparisons**             | `=, !=, <, >, <=, >=`                     | All comparison operators |
| **Boolean logic**           | `AND, OR, NOT`                            | Boolean operators        |
| **NULL checks**             | `IS NULL, IS NOT NULL`                    | NULL handling            |
| **IN clause**               | `col IN (1, 2, 3)`                        | Value lists              |
| **Table-qualified columns** | `table.col`                               | Column references        |

### ❌ Not Supported

| Feature                | Why Not Supported                      |
| ---------------------- | -------------------------------------- |
| **GROUP BY**           | No aggregation support                 |
| **Aggregations**       | COUNT, SUM, AVG, etc. not implemented  |
| **ORDER BY**           | No sorting support                     |
| **HAVING**             | Requires GROUP BY                      |
| **LIMIT**              | Not implemented                        |
| **UNION**              | Not implemented                        |
| **Subqueries**         | Not implemented                        |
| **CTEs**               | Common Table Expressions not supported |
| **Non-equality joins** | Only `=` joins supported               |
| **Arithmetic**         | No `+`, `-`, `*`, `/` in expressions   |
| **Functions**          | No SQL functions (except literals)     |
| **Window functions**   | Not supported                          |

---

## Advanced Features

### 1. **Debug Mode**

Enable debug mode to see execution details:

```python
engine = Engine(debug=True)

for row in engine.query("SELECT * FROM users"):
    print(row)
```

**Output:**

```
============================================================
STREAMING SQL ENGINE - DEBUG MODE
============================================================

[1/3] PARSING SQL QUERY...
Query:
SELECT * FROM users

✓ SQL parsed successfully

[2/3] BUILDING LOGICAL PLAN...
✓ Logical plan built:
  - Root table: users (alias: None)
  - Joins: 0
  - WHERE clause: No
  - Projections: 1

[3/3] EXECUTING QUERY...
Building execution pipeline...

  [SCAN] Scanning table: users
      Started reading from users
  [PROJECT] Applying SELECT projection

Pipeline ready. Starting row processing...

------------------------------------------------------------
{'id': 1, 'name': 'Alice'}
{'id': 2, 'name': 'Bob'}
```

### 2. **JSONL Mode**

Use JSONL mode for simpler execution (lower CPU usage):

```python
engine = Engine(use_jsonl_mode=True)

# Same queries work, but execution is different
for row in engine.query("SELECT * FROM users"):
    print(row)
```

**When to use JSONL mode:**

- Complex queries with multiple joins
- Want lower CPU usage
- Don't need real-time streaming

**When NOT to use JSONL mode:**

- Need true streaming (row-by-row)
- Memory-constrained environments
- Very large datasets

### 3. **Merge Joins**

Optimize joins when both tables are sorted:

```python
# Register sorted sources
engine.register("users", users_source, ordered_by="id")
engine.register("orders", orders_source, ordered_by="user_id")

# Engine will use merge join (more memory efficient)
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
"""
```

**Benefits:**

- Lower memory usage
- Better performance for sorted data
- No need to build lookup index

### 4. **Database Connection Pools**

Use connection pools for efficient database access:

```python
from streaming_sql_engine import create_pool_from_env, create_table_source

# Create pool from environment variables
pool = create_pool_from_env()

# Register multiple tables from same database
engine.register("users", create_table_source(pool, "users"))
engine.register("orders", create_table_source(pool, "orders"))

# Clean up when done
pool.closeall()
```

**Environment variables (.env file):**

```env
db_host=localhost
db_port=5432
db_user=myuser
db_password=mypassword
db_name=mydatabase
```

### 5. **Custom WHERE Clauses in Sources**

Filter data at the source level:

```python
# PostgreSQL
engine.register(
    "active_users",
    create_table_source(pool, "users", where_clause="active = true")
)

# MySQL
engine.register(
    "recent_orders",
    create_table_source(mysql_pool, "orders", where_clause="created_at > '2024-01-01'")
)
```

### 6. **Streaming Large Datasets**

Process large datasets without loading everything:

```python
def large_dataset():
    """Generate or fetch large dataset."""
    # This could be millions of rows
    for i in range(1, 10000000):
        yield {"id": i, "value": process(i)}

engine.register("large_table", large_dataset)

# Process row-by-row without loading all into memory
for row in engine.query("SELECT * FROM large_table WHERE value > 100"):
    process_row(row)
```

---

## Common Patterns

### Pattern 1: Join Database + API

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
import requests

pool = create_pool_from_env()
engine = Engine()

# Database source
engine.register(
    "products",
    create_table_source(pool, "products")
)

# API source
def prices_api():
    response = requests.get("https://api.example.com/prices")
    for item in response.json():
        yield item

engine.register("prices", prices_api)

# Join query
query = """
    SELECT products.name, prices.amount
    FROM products
    JOIN prices ON products.sku = prices.sku
"""

for row in engine.query(query):
    print(f"{row['name']}: ${row['amount']}")
```

### Pattern 2: Join Multiple Databases

```python
from streaming_sql_engine import (
    Engine,
    create_pool_from_env,
    create_mysql_pool_from_env,
    create_table_source
)

# PostgreSQL pool
pg_pool = create_pool_from_env()

# MySQL pool
mysql_pool = create_mysql_pool_from_env()

engine = Engine()

# Register from different databases
engine.register("pg_users", create_table_source(pg_pool, "users"))
engine.register("mysql_orders", create_table_source(mysql_pool, "orders"))

# Join across databases
query = """
    SELECT u.name, o.total
    FROM pg_users u
    JOIN mysql_orders o ON u.id = o.user_id
"""
```

### Pattern 3: Join Database + CSV

```python
import csv
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source

pool = create_pool_from_env()
engine = Engine()

# Database source
engine.register("users", create_table_source(pool, "users"))

# CSV source
def read_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

engine.register("departments", lambda: read_csv("departments.csv"))

# Join
query = """
    SELECT users.name, departments.name AS dept
    FROM users
    JOIN departments ON users.dept_id = departments.id
"""
```

### Pattern 4: Real-time API Joins

```python
import requests
import time

def live_api_source():
    """Stream live data from API."""
    while True:
        response = requests.get("https://api.example.com/live-data")
        for item in response.json():
            yield item
        time.sleep(1)  # Poll every second

engine.register("live_data", live_api_source)
engine.register("reference_data", reference_source)

query = """
    SELECT live_data.value, reference_data.name
    FROM live_data
    JOIN reference_data ON live_data.id = reference_data.id
"""

# Process live data as it arrives
for row in engine.query(query):
    process_live_row(row)
```

### Pattern 5: Filtered Joins

```python
# Filter at source level
engine.register(
    "active_users",
    create_table_source(pool, "users", where_clause="active = true")
)

# Filter in WHERE clause
query = """
    SELECT u.name, o.total
    FROM active_users u
    JOIN orders o ON u.id = o.user_id
    WHERE o.total > 100
"""
```

### Pattern 6: Multiple Joins

```python
query = """
    SELECT
        users.name,
        orders.total,
        products.name AS product_name,
        categories.name AS category_name
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN products ON orders.product_id = products.id
    JOIN categories ON products.category_id = categories.id
    WHERE users.active = true
"""
```

---

## Best Practices

### 1. **Use Generators for Large Datasets**

✅ **Good:**

```python
def large_source():
    for i in range(1000000):
        yield {"id": i}
```

❌ **Bad:**

```python
def large_source():
    return iter([{"id": i} for i in range(1000000)])  # Loads all into memory
```

### 2. **Register Smaller Table First for Joins**

For better performance, register the smaller table as the lookup side:

✅ **Good:**

```python
# Small lookup table
engine.register("categories", categories_source)  # 100 rows
# Large table
engine.register("products", products_source)  # 1M rows

query = """
    SELECT products.name, categories.name
    FROM products
    JOIN categories ON products.category_id = categories.id
"""
```

### 3. **Use `ordered_by` for Sorted Data**

If your data is sorted, register it for merge join optimization:

```python
engine.register("users", users_source, ordered_by="id")
```

### 4. **Filter at Source Level When Possible**

Filter data in the source function or use `where_clause`:

✅ **Good:**

```python
engine.register(
    "active_users",
    create_table_source(pool, "users", where_clause="active = true")
)
```

❌ **Less efficient:**

```python
engine.register("users", create_table_source(pool, "users"))
# Filter in WHERE clause (processes all rows first)
```

### 5. **Handle Errors Gracefully**

```python
try:
    for row in engine.query(query):
        process_row(row)
except Exception as e:
    print(f"Error: {e}")
    # Handle error
```

### 6. **Clean Up Resources**

```python
pool = create_pool_from_env()
try:
    # Use pool
    engine.register("users", create_table_source(pool, "users"))
    # ... queries ...
finally:
    pool.closeall()  # Always clean up
```

### 7. **Use Debug Mode for Development**

```python
# Development
engine = Engine(debug=True)

# Production
engine = Engine(debug=False)
```

---

## Troubleshooting

### Error: "Table 'X' is not registered"

**Problem:** You're using a table name in SQL that wasn't registered.

**Solution:**

```python
# Make sure you register before querying
engine.register("users", users_source)
# Now you can use it
engine.query("SELECT * FROM users")
```

### Error: "Column 'X' not found in row"

**Problem:** The column doesn't exist in the data source.

**Solution:**

```python
# Check your source function returns the right columns
def users_source():
    return iter([
        {"id": 1, "name": "Alice"},  # Make sure 'name' exists
    ])
```

### Error: "Only equality joins are supported"

**Problem:** You're using a non-equality join condition.

**Solution:**

```python
# ✅ Good: Equality join
JOIN orders ON users.id = orders.user_id

# ❌ Bad: Non-equality join
JOIN orders ON users.id > orders.user_id  # Not supported
```

### Error: "GROUP BY is not supported"

**Problem:** You're trying to use unsupported SQL features.

**Solution:**

```python
# ❌ Not supported
SELECT category, COUNT(*) FROM products GROUP BY category

# ✅ Workaround: Do aggregation in Python
for row in engine.query("SELECT category, price FROM products"):
    # Aggregate in Python
    aggregate_by_category(row)
```

### Performance Issues

**Problem:** Query is slow.

**Solutions:**

1. **Use merge joins** if data is sorted:

   ```python
   engine.register("table", source, ordered_by="id")
   ```

2. **Filter at source level:**

   ```python
   create_table_source(pool, "table", where_clause="...")
   ```

3. **Register smaller table first** for joins

4. **Use JSONL mode** for complex queries:
   ```python
   engine = Engine(use_jsonl_mode=True)
   ```

### Memory Issues

**Problem:** Using too much memory.

**Solutions:**

1. **Use generators** instead of lists
2. **Process results immediately** (don't collect all rows)
3. **Use merge joins** for sorted data
4. **Filter early** at source level

---

## Examples

### Example 1: Simple Join

```python
from streaming_sql_engine import Engine

engine = Engine()

def users():
    return iter([
        {"id": 1, "name": "Alice", "dept_id": 10},
        {"id": 2, "name": "Bob", "dept_id": 20},
    ])

def departments():
    return iter([
        {"id": 10, "name": "Engineering"},
        {"id": 20, "name": "Sales"},
    ])

engine.register("users", users)
engine.register("departments", departments)

query = """
    SELECT users.name, departments.name AS dept_name
    FROM users
    JOIN departments ON users.dept_id = departments.id
"""

for row in engine.query(query):
    print(row)
```

### Example 2: Database + API Join

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
import requests
from dotenv import load_dotenv

load_dotenv()

pool = create_pool_from_env()
engine = Engine()

# Database source
engine.register("products", create_table_source(pool, "products"))

# API source
def prices():
    response = requests.get("https://api.example.com/prices")
    return iter(response.json())

engine.register("prices", prices)

# Join
query = """
    SELECT products.name, prices.amount
    FROM products
    JOIN prices ON products.sku = prices.sku
    WHERE prices.amount > 100
"""

for row in engine.query(query):
    print(f"{row['name']}: ${row['amount']}")

pool.closeall()
```

### Example 3: Multiple Joins

```python
from streaming_sql_engine import Engine

engine = Engine()

# Define sources
def users():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ])

def orders():
    return iter([
        {"id": 101, "user_id": 1, "product_id": 501, "total": 50.00},
        {"id": 102, "user_id": 2, "product_id": 502, "total": 75.00},
    ])

def products():
    return iter([
        {"id": 501, "name": "Widget"},
        {"id": 502, "name": "Gadget"},
    ])

# Register
engine.register("users", users)
engine.register("orders", orders)
engine.register("products", products)

# Multiple joins
query = """
    SELECT
        users.name AS user_name,
        products.name AS product_name,
        orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN products ON orders.product_id = products.id
    WHERE orders.total > 60
"""

for row in engine.query(query):
    print(row)
```

### Example 4: LEFT JOIN

```python
from streaming_sql_engine import Engine

engine = Engine()

def users():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ])

def orders():
    return iter([
        {"id": 101, "user_id": 1, "total": 50.00},
        {"id": 102, "user_id": 2, "total": 75.00},
        # User 3 has no orders
    ])

engine.register("users", users)
engine.register("orders", orders)

# LEFT JOIN: Include users even without orders
query = """
    SELECT users.name, orders.total
    FROM users
    LEFT JOIN orders ON users.id = orders.user_id
"""

for row in engine.query(query):
    print(row)
# Output:
# {'name': 'Alice', 'total': 50.0}
# {'name': 'Bob', 'total': 75.0}
# {'name': 'Charlie', 'total': None}  # NULL for users without orders
```

### Example 5: Complex WHERE Clause

```python
from streaming_sql_engine import Engine

engine = Engine()

def products():
    return iter([
        {"id": 1, "name": "Widget", "price": 10.99, "category": "A", "stock": 5},
        {"id": 2, "name": "Gadget", "price": 19.99, "category": "B", "stock": 0},
        {"id": 3, "name": "Thing", "price": 5.99, "category": "A", "stock": 10},
    ])

engine.register("products", products)

# Complex WHERE with AND, OR, IN
query = """
    SELECT name, price
    FROM products
    WHERE (price > 10 AND stock > 0)
       OR category IN ('A', 'B')
"""

for row in engine.query(query):
    print(row)
```

---

## Quick Reference

### Engine API

```python
from streaming_sql_engine import Engine

# Create engine
engine = Engine(debug=False, use_jsonl_mode=False)

# Register source
engine.register(table_name, source_fn, ordered_by=None)

# Execute query
results = engine.query(sql_string)
for row in results:
    # Process row
    pass
```

### Database Helpers

```python
from streaming_sql_engine import (
    create_pool_from_env,           # PostgreSQL pool
    create_mysql_pool_from_env,      # MySQL pool
    create_table_source,             # Table source from pool
    stream_query,                    # Custom SQL query
)

# PostgreSQL
pool = create_pool_from_env()
source = create_table_source(pool, "table", where_clause="...", order_by="...")

# MySQL
mysql_pool = create_mysql_pool_from_env()
source = create_table_source(mysql_pool, "table")
```

### Supported SQL Syntax

```sql
-- SELECT
SELECT col1, col2, col3 AS alias
SELECT table.col
SELECT *

-- FROM
FROM table
FROM table AS alias

-- JOIN
JOIN table ON left.key = right.key
LEFT JOIN table ON left.key = right.key

-- WHERE
WHERE col = value
WHERE col > value
WHERE col IS NULL
WHERE col IN (val1, val2)
WHERE condition AND condition
WHERE condition OR condition
WHERE NOT condition
```

---

## Next Steps

- **Examples**: See `examples/` directory for more examples
- **Technical Details**: Read [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
- **Performance**: See [PERFORMANCE.md](PERFORMANCE.md)
- **Database Integration**: See [MYSQL_USAGE.md](MYSQL_USAGE.md)

---

## Summary

The Streaming SQL Engine lets you:

1. ✅ **Join different data sources** (databases, APIs, files)
2. ✅ **Use SQL syntax** for familiar querying
3. ✅ **Process row-by-row** for memory efficiency
4. ✅ **Integrate easily** with Python applications

**Key Concepts:**

- Register data sources as Python functions
- Execute SQL queries with joins
- Process results as generators
- Use for cross-system data integration

**Best For:**

- Cross-system joins (MySQL + PostgreSQL + API)
- Python application integration
- Rapid prototyping
- Simple joins (no aggregations needed)

**Not For:**

- Complex analytics (use DuckDB/Spark)
- Same-database queries (use direct SQL)
- Big data (use distributed systems)

Happy coding! 🚀

