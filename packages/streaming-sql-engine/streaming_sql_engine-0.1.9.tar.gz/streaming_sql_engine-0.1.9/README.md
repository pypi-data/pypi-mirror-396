# Streaming SQL Engine

A lightweight Python library that executes SQL queries **row-by-row** across **any data source** - databases, APIs, files, or custom Python functions. Join data from different systems using standard SQL syntax, without loading everything into memory.

## 🎯 What It Does

**Execute SQL queries that join data from multiple sources:**

- ✅ **Databases** (PostgreSQL, MySQL, MongoDB)
- ✅ **REST APIs** (any HTTP endpoint)
- ✅ **Files** (JSONL, CSV, JSON)
- ✅ **Custom Python functions** (any iterator)

**All in one SQL query, streaming results row-by-row.**

---

## 🚀 Why It's Useful

### Problem: You Can't Join Across Different Systems

**Traditional databases can't do this:**

```python
# ❌ Can't join MySQL + PostgreSQL + REST API in one query
# ❌ Can't join database + CSV file
# ❌ Can't join API + JSON file
```

**This library solves it:**

```python
# ✅ Join MySQL + PostgreSQL + REST API + CSV file
# ✅ All in one SQL query
# ✅ Streams results row-by-row (low memory)
```

### Key Benefits

1. **Cross-System Joins** - Join data from completely different sources
2. **Memory Efficient** - Processes row-by-row, never loads full tables
3. **Zero Infrastructure** - No clusters, no setup, just Python
4. **Automatic Optimizations** - Filter pushdown, column pruning, vectorized operations
5. **Simple API** - Standard SQL syntax, easy to use

---

## 📦 Installation

```bash
pip install streaming-sql-engine
```

**Or install from source:**

```bash
git clone <repository>
cd streaming_sql_engine
pip install -e .
```

---

## 💡 Quick Start

### Example 1: Simple Join

```python
from streaming_sql_engine import Engine

# Create engine
engine = Engine()

# Register data sources (any Python iterators)
def users_source():
    return iter([
        {"id": 1, "name": "Alice", "dept_id": 10},
        {"id": 2, "name": "Bob", "dept_id": 20},
    ])

def departments_source():
    return iter([
        {"id": 10, "name": "Engineering"},
        {"id": 20, "name": "Sales"},
    ])

engine.register("users", users_source)
engine.register("departments", departments_source)

# Execute SQL query
query = """
    SELECT users.name, departments.name AS dept
    FROM users
    JOIN departments ON users.dept_id = departments.id
"""

for row in engine.query(query):
    print(row)
# Output:
# {'users.name': 'Alice', 'departments.name': 'Engineering'}
# {'users.name': 'Bob', 'departments.name': 'Sales'}
```

### Example 2: Join Database + API + File

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_table_source, create_pool_from_env
import requests
import json

engine = Engine()

# 1. Database source (PostgreSQL)
pool = create_pool_from_env()
engine.register(
    "products",
    create_table_source(pool, "products")
)

# 2. REST API source
def api_customers():
    response = requests.get("https://api.example.com/customers")
    for item in response.json():
        yield item

engine.register("customers", api_customers)

# 3. JSONL file source
def file_orders():
    with open("orders.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("orders", file_orders, filename="orders.jsonl")

# Join all three sources!
query = """
    SELECT
        products.name,
        customers.email,
        orders.quantity
    FROM products
    JOIN customers ON products.customer_id = customers.id
    JOIN orders ON products.id = orders.product_id
    WHERE products.price > 100
"""

for row in engine.query(query):
    print(row)
```

### Example 3: Simple Protocol Support (Automated!)

**Use helper functions - no manual implementation needed:**

```python
from streaming_sql_engine import Engine
from streaming_sql_engine.protocol_helpers import (
    register_file_source,
    register_api_source,
)

engine = Engine()

# Register file sources with automatic protocol support
register_file_source(engine, "products", "data/products.jsonl")
register_file_source(engine, "categories", "data/categories.csv")

# Register API source with automatic protocol support
register_api_source(engine, "customers", "http://localhost:8000", "customers")

# Query with automatic optimizations (filter pushdown, column pruning)
for row in engine.query("""
    SELECT products.name, categories.name AS category
    FROM products
    JOIN categories ON products.category_id = categories.id
    WHERE products.price > 100
"""):
    print(row)
```

**That's it!** No manual SQL parsing, no manual filtering - everything is automatic! 🎉

See [Simple Protocol Guide](documentation/SIMPLE_PROTOCOL_GUIDE.md) for more details.

---

## 🎯 Use Cases

### ✅ Perfect For

1. **Cross-System Data Integration**

   - Join MySQL + PostgreSQL + MongoDB
   - Join database + REST API
   - Join API + CSV file

2. **Real-Time Data Processing**

   - Stream data from multiple sources
   - Process row-by-row without buffering
   - Low memory footprint

3. **Data Pipeline ETL**

   - Transform data from multiple sources
   - Join before loading to destination
   - Python-native processing

4. **Microservices Data Aggregation**
   - Join data from multiple services
   - No shared database needed
   - Simple Python integration

### ❌ Not For

- **Single Database Queries** - Use direct SQL (10-100x faster)
- **Complex SQL** - GROUP BY, aggregations, subqueries not supported
- **Maximum Performance** - For same-database joins, use database directly

---

## 🔧 Features

### Supported SQL

- ✅ **SELECT** - Column selection, aliasing
- ✅ **FROM** - Single table, aliases
- ✅ **JOIN** - INNER JOIN, LEFT JOIN
- ✅ **WHERE** - Comparisons, boolean logic, NULL checks, IN clauses
- ✅ **Table-qualified columns** - `table.column`

### Not Supported

- ❌ GROUP BY, aggregations
- ❌ ORDER BY
- ❌ HAVING
- ❌ UNION
- ❌ Subqueries
- ❌ Non-equality joins

---

## ⚡ Performance Optimizations

### 1. Protocol-Based Optimizations (Automatic)

**Filter Pushdown** - Push WHERE clauses to data sources:

```python
# Engine automatically passes WHERE clause to source
def source(dynamic_where=None, dynamic_columns=None):
    query = f"SELECT * FROM table WHERE {dynamic_where}"
    # Source filters before returning data
```

**Column Pruning** - Only request needed columns:

```python
# Engine automatically requests only needed columns
def source(dynamic_where=None, dynamic_columns=None):
    columns = ", ".join(dynamic_columns)  # Only requested columns
    query = f"SELECT {columns} FROM table"
```

**How it works:** Engine detects if your source function accepts `dynamic_where`/`dynamic_columns` parameters automatically. No flags needed!

**💡 Tip:** Use helper functions to automate protocol support - see [Simple Protocol Guide](documentation/SIMPLE_PROTOCOL_GUIDE.md)!

### 2. Polars Vectorization (Automatic)

**10-200x faster** for large datasets:

- Vectorized filtering (SIMD-accelerated)
- Vectorized projections
- Batch processing

Enabled by default. Disable with:

```python
engine = Engine(use_polars=False)
```

### 3. Memory-Mapped Joins (For Files)

**90-99% memory reduction** for large JSONL files:

```python
engine.register(
    "products",
    lambda: read_jsonl("products.jsonl"),
    filename="products.jsonl"  # Enables mmap joins
)
```

### 4. Merge Joins (For Sorted Data)

**Efficient joins** when both sides are sorted:

```python
engine.register(
    "users",
    users_source,
    ordered_by="id"  # Enables merge join
)
```

---

## 📚 Examples

### Database + Database

```python
from examples.database_helpers import create_table_source, create_pool_from_env

# PostgreSQL
pg_pool = create_postgresql_pool_from_env()
engine.register("pg_users", create_table_source(pg_pool, "users"))

# MySQL
mysql_pool = create_mysql_pool_from_env()
engine.register("mysql_orders", create_table_source(mysql_pool, "orders"))

# Join across databases!
query = """
    SELECT pg_users.name, mysql_orders.total
    FROM pg_users
    JOIN mysql_orders ON pg_users.id = mysql_orders.user_id
"""
```

### Database + REST API

```python
import requests

def api_products():
    response = requests.get("https://api.example.com/products")
    return iter(response.json())

engine.register("api_products", api_products)
engine.register("db_orders", create_table_source(pool, "orders"))

query = """
    SELECT api_products.name, db_orders.quantity
    FROM api_products
    JOIN db_orders ON api_products.id = db_orders.product_id
"""
```

### File + File

```python
def read_jsonl(filename):
    with open(filename) as f:
        for line in f:
            yield json.loads(line)

engine.register("products", lambda: read_jsonl("products.jsonl"), filename="products.jsonl")
engine.register("images", lambda: read_jsonl("images.jsonl"), filename="images.jsonl")

query = """
    SELECT products.name, images.url
    FROM products
    JOIN images ON products.id = images.product_id
"""
```

---

## 🏗️ Architecture

### How It Works

```
SQL Query
    ↓
Parser (sqlglot) → AST
    ↓
Planner → Logical Plan
    ↓
Optimizer → Optimized Plan (column pruning, filter pushdown)
    ↓
Executor → Iterator Pipeline
    ↓
Results (Generator) → Row-by-row streaming
```

### Iterator Pipeline

```
ScanIterator → FilterIterator → JoinIterators → ProjectIterator
```

Each iterator processes rows incrementally, never loading full tables.

---

## 🔍 Debug Mode

Enable debug output to see execution details:

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
✓ SQL parsed successfully

[2/3] BUILDING LOGICAL PLAN...
✓ Logical plan built:
  - Root table: users
  - Joins: 1
  - WHERE clause: Yes
  - Projections: 2

[3/3] EXECUTING QUERY...
  [OPTIMIZATION] Source supports protocol - applying column pruning
  [SCAN] Scanning table: users
  [JOIN] INNER JOIN orders
  [PROJECT] Applying SELECT projection
```

---

## 📖 Documentation

- **[Quick Start Guide](documentation/QUICK_START.md)** - Get started in 5 minutes
- **[User Guide](documentation/USER_GUIDE.md)** - Complete usage guide
- **[Best Use Cases](documentation/BEST_USE_CASES.md)** - When to use this library
- **[Performance Guide](documentation/PERFORMANCE.md)** - Performance tips and benchmarks
- **[Migration Guide](documentation/MIGRATION_GUIDE.md)** - Upgrading from older versions
- **[Developer Guide](documentation/DEVELOPER_GUIDE.md)** - Contributing and extending

---

## 🎓 Key Concepts

### Protocol-Based Optimization

**No flags needed!** The engine automatically detects if your source supports optimizations:

```python
# Simple source (no optimizations)
def simple_source():
    return iter([...])

# Optimized source (with protocol)
def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Engine automatically passes optimization parameters
    ...
```

### Streaming Execution

**Row-by-row processing:**

- Results are yielded immediately as they're produced
- Never loads full tables into memory
- Perfect for large datasets

### Cross-Source Joins

**Join any data sources:**

- Databases (PostgreSQL, MySQL, MongoDB)
- APIs (REST, GraphQL, any HTTP endpoint)
- Files (JSONL, CSV, JSON)
- Custom Python functions

---

## 🤝 Contributing

Contributions welcome! See [Developer Guide](documentation/DEVELOPER_GUIDE.md) for details.

---

## 📄 License

MIT

---

## 🙋 FAQ

**Q: Can I join data from different databases?**  
A: Yes! That's the main use case. Join MySQL + PostgreSQL + MongoDB in one query.

**Q: Is it faster than database queries?**  
A: No. For same-database queries, use direct SQL (10-100x faster). This library is for cross-system joins.

**Q: Does it support GROUP BY?**  
A: No. Use a database for aggregations. This library focuses on joins and filtering.

**Q: How does it handle large datasets?**  
A: Streams row-by-row, uses memory-mapped files for large JSONL files, and Polars for vectorized operations.

**Q: Can I use it with APIs?**  
A: Yes! Any Python function that returns an iterator works. Perfect for REST APIs.

---

## ⭐ Why Use This?

**Use this library when:**

- ✅ You need to join data from different systems
- ✅ You want to process data row-by-row (low memory)
- ✅ You need Python-native data processing
- ✅ You want simple SQL syntax for complex data integration

**Don't use this library when:**

- ❌ All data is in the same database (use direct SQL)
- ❌ You need GROUP BY or aggregations (use database)
- ❌ You need maximum performance for same-database queries (use database)

---

**Ready to get started?** Check out the [Quick Start Guide](documentation/QUICK_START.md)!
