# Streaming SQL Join Engine - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture & Implementation](#architecture--implementation)
3. [Design Inspiration](#design-inspiration)
4. [Comparison with Similar Tools](#comparison-with-similar-tools)
5. [Capabilities](#capabilities)
6. [Why Use This Library](#why-use-this-library)
7. [How to Use](#how-to-use)
8. [Technical Deep Dive](#technical-deep-dive)

---

## Overview

The **Streaming SQL Join Engine** is a Python library that enables SQL-style joins across heterogeneous data sources. Unlike traditional databases that require all data to be in one place, this engine allows you to join data from:

- **Databases** (MySQL, PostgreSQL)
- **APIs** (REST, GraphQL, gRPC)
- **Files** (CSV, JSONL, JSON)
- **Any Python iterable**

All using standard SQL syntax, with zero infrastructure requirements.

### Key Characteristics

- **Streaming**: Processes data row-by-row, never loading full tables
- **Cross-system**: Join data from completely different sources
- **Python-native**: Easy integration with Python ecosystem
- **Zero-config**: No clusters, no infrastructure, just Python

---

## Architecture & Implementation

### Core Design Philosophy

The engine follows a **pipeline architecture** inspired by database query execution engines, but implemented in pure Python using iterators.

### Implementation Layers

```
┌─────────────────────────────────────────────────────────┐
│                    SQL Query String                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  [1] PARSER (sqlglot)                                   │
│      • Parses SQL into Abstract Syntax Tree (AST)       │
│      • Validates supported features                     │
│      • Multi-dialect support (MySQL, PostgreSQL, SQLite)│
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  [2] PLANNER                                            │
│      • Converts AST to LogicalPlan                     │
│      • Extracts: FROM, JOINs, WHERE, SELECT             │
│      • Validates table registrations                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  [3] EXECUTOR                                           │
│      • Builds iterator pipeline                        │
│      • Chains operators together                       │
│      • Returns generator (lazy evaluation)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│  [4] OPERATORS (Iterator Chain)                         │
│      • ScanIterator: Read from source                  │
│      • FilterIterator: Apply WHERE clause               │
│      • LookupJoinIterator: Hash-based joins            │
│      • MergeJoinIterator: Sorted merge joins           │
│      • ProjectIterator: Apply SELECT projection        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Results (Python Generator)                 │
└─────────────────────────────────────────────────────────┘
```

### Python Implementation Details

#### 1. **Iterator-Based Pipeline**

The entire engine is built on Python's iterator protocol, enabling lazy evaluation:

```python
class ScanIterator:
    """Reads rows from a source."""
    def __init__(self, source_fn, table_name, alias):
        self.source = source_fn()
        self.table_name = table_name
        self.alias = alias

    def __next__(self):
        row = next(self.source)
        # Prefix columns with table alias
        return {f"{self.alias}.{k}": v for k, v in row.items()}
```

**Why Iterators?**

- **Memory efficient**: Only one row in memory at a time
- **Lazy evaluation**: Processing starts only when you iterate
- **Composable**: Can chain iterators together
- **Pythonic**: Uses standard Python patterns

#### 2. **Join Algorithms**

**Lookup Join (Hash Join):**

```python
class LookupJoinIterator:
    def _build_index(self):
        # Build hash index from right table
        for row in self.right_source():
            key = row[join_key]
            self.lookup_index[key].append(row)

    def __next__(self):
        left_row = next(self.left_source)
        key = left_row[left_join_key]
        matches = self.lookup_index.get(key, [])
        return {**left_row, **matches[0]}
```

**Merge Join:**

```python
class MergeJoinIterator:
    def __next__(self):
        # Both sides sorted by join key
        # Merge like two sorted lists
        if left_key == right_key:
            return {**left_row, **right_row}
        elif left_key < right_key:
            advance_left()
        else:
            advance_right()
```

#### 3. **Expression Evaluation**

Recursive tree traversal for WHERE clauses and SELECT projections:

```python
def evaluate_expression(expr, row):
    if isinstance(expr, exp.Column):
        return row[f"{expr.table}.{expr.name}"]
    elif isinstance(expr, exp.EQ):
        left = evaluate_expression(expr.this, row)
        right = evaluate_expression(expr.expression, row)
        return left == right
    elif isinstance(expr, exp.And):
        left = evaluate_expression(expr.this, row)
        if not left:  # Short-circuit
            return False
        right = evaluate_expression(expr.expression, row)
        return bool(right)
    # ... more expression types
```

**Optimizations:**

- Type caching for faster `isinstance()` checks
- Short-circuit evaluation for AND/OR
- Type coercion for comparisons (handles string vs number)

#### 4. **Source Abstraction**

Any Python function that returns an iterator can be a source:

```python
# Database source
def db_source():
    return stream_query(pool, "SELECT * FROM table")

# API source
def api_source():
    response = requests.get("https://api.com/data")
    for item in response.json():
        yield transform(item)

# File source
def file_source():
    with open("data.jsonl") as f:
        for line in f:
            yield json.loads(line)

# All work the same way!
engine.register("table1", db_source)
engine.register("table2", api_source)
engine.register("table3", file_source)
```

---

## Design Inspiration

### 1. **Volcano Model (Iterator Model)** ⭐ Primary Inspiration

**Source:** "The Volcano Optimizer Generator: Extensibility and Efficient Search" by Goetz Graefe (1993)

The **Volcano Model** is the foundation of this engine's architecture:

**Core Concept:**

- Each operator implements `next()` method
- Operators are chained together
- Data flows through the pipeline row-by-row
- Enables pipelined execution (no materialization)

**Implementation in Python:**

```python
class ScanIterator:
    def __next__(self):
        return next(self.source)  # Get next row

class FilterIterator:
    def __next__(self):
        while True:
            row = next(self.source)
            if evaluate_expression(self.where_expr, row):
                return row  # Only yield matching rows

class LookupJoinIterator:
    def __next__(self):
        left_row = next(self.left_source)
        key = left_row[left_key]
        right_row = self.lookup_index[key]
        return {**left_row, **right_row}  # Merge rows
```

**Why This Model:**

- ✅ **Memory efficient**: Only one row in memory at a time
- ✅ **Composable**: Operators can be chained arbitrarily
- ✅ **Extensible**: Easy to add new operators
- ✅ **Lazy**: Processing starts only when iterated

**References:**

- Graefe, G. (1993). "The Volcano Optimizer Generator: Extensibility and Efficient Search"
- Graefe, G. (1990). "Encapsulation of Parallelism in the Volcano Query Processing System"

---

### 2. **PostgreSQL Query Executor**

**Inspiration:** PostgreSQL's executor architecture

**Concepts Adopted:**

- **Logical vs Physical Plans**: Separate planning from execution
- **Join Algorithms**: Hash join and merge join implementations
- **Expression Evaluation**: Recursive tree traversal
- **Column Prefixing**: Table-qualified column names

**PostgreSQL's Approach:**

```
Query → Parser → Planner → Executor → Operators → Results
```

**Our Implementation:**

```
SQL → Parser → Planner → Executor → Iterator Pipeline → Results
```

**Key Differences:**

- PostgreSQL: C code, compiled, very fast
- Our Engine: Python, interpreted, but flexible

---

### 3. **SQLite Query Execution Model**

**Inspiration:** SQLite's simple, efficient query execution

**Concepts Adopted:**

- **Simple join algorithms**: Hash-based lookups
- **Expression evaluation**: Recursive AST traversal
- **Memory efficiency**: Minimal memory footprint

**SQLite's VDBE (Virtual Database Engine):**

- Bytecode-based execution
- Simple, efficient operators
- Low memory overhead

**Our Adaptation:**

- Python iterators instead of bytecode
- Same simplicity and efficiency goals
- Python-native implementation

---

### 4. **Apache Flink Streaming Architecture**

**Inspiration:** Flink's streaming data processing model

**Concepts Adopted:**

- **Row-by-row processing**: Process data as it arrives
- **Stateful operations**: Maintain join state (lookup indexes)
- **Incremental processing**: Only process new/changed data
- **Event-time processing**: Handle streaming data sources

**Flink's Approach:**

- Stream processing with state management
- Low-latency processing
- Event-time semantics

**Our Adaptation:**

- Simplified for Python
- No distributed processing
- Focus on cross-system joins

---

### 5. **Python Iterator Protocol (PEP 234)**

**Inspiration:** Python's built-in iterator protocol

**Core Concept:**

- Objects that implement `__iter__()` and `__next__()`
- Lazy evaluation (compute on demand)
- Composable (can chain iterators)

**Python Patterns Used:**

```python
# Generator functions
def source():
    for item in data:
        yield item

# Iterator chaining
filtered = filter(predicate, source())
mapped = map(transform, filtered)

# Our implementation
scan = ScanIterator(source)
filtered = FilterIterator(scan, where_expr)
joined = LookupJoinIterator(filtered, right_source, ...)
```

**Why This Works:**

- ✅ **Pythonic**: Uses standard Python patterns
- ✅ **Composable**: Easy to chain operations
- ✅ **Memory efficient**: Lazy evaluation
- ✅ **Familiar**: Python developers understand iterators

---

### 6. **Functional Programming Patterns**

**Inspiration:** Functional programming principles

**Concepts Adopted:**

- **Immutable data**: Rows are dictionaries (effectively immutable)
- **Higher-order functions**: Operators are composable functions
- **Pure functions**: Expression evaluation is side-effect-free
- **Pipeline composition**: Chain operations together

**Functional Patterns:**

```python
# Pipeline composition
pipeline = (
    source()
    .filter(where_clause)
    .join(right_source)
    .project(select_columns)
)

# Our implementation (similar concept)
iterator = ScanIterator(source)
iterator = FilterIterator(iterator, where_expr)
iterator = LookupJoinIterator(iterator, right_source, ...)
iterator = ProjectIterator(iterator, projections)
```

---

### 7. **Database Join Algorithms (Academic Literature)**

**Inspiration:** Classic database join algorithms

**Hash Join (Lookup Join):**

- **Source**: Database systems literature
- **Algorithm**: Build hash index on right table, probe with left table
- **Complexity**: O(n + m) where n = left size, m = right size
- **Our Implementation**: `LookupJoinIterator`

**Merge Join:**

- **Source**: Database systems literature
- **Algorithm**: Merge two sorted lists
- **Complexity**: O(n + m) but better cache locality
- **Our Implementation**: `MergeJoinIterator`

**References:**

- "Database System Concepts" (Silberschatz, Korth, Sudarshan)
- "The Design and Implementation of Modern Column-Oriented Database Systems"

---

## Comparison with Similar Tools

### vs DuckDB

| Feature                | Streaming SQL Engine             | DuckDB                                  |
| ---------------------- | -------------------------------- | --------------------------------------- |
| **Language**           | Python                           | C++                                     |
| **Performance**        | Slower (Python)                  | Very fast (C++)                         |
| **SQL Support**        | Limited (joins, WHERE, SELECT)   | Full SQL (GROUP BY, aggregations, etc.) |
| **Cross-system joins** | ✅ Excellent (any Python source) | ⚠️ Limited (needs connectors)           |
| **Infrastructure**     | None (pure Python)               | None (embedded)                         |
| **Real-time sources**  | ✅ Native support                | ❌ Batch-oriented                       |
| **Python processing**  | ✅ Full Python ecosystem         | ⚠️ Limited                              |
| **Use case**           | Cross-system integration         | Analytics on files/databases            |

**When to use DuckDB:**

- Fast analytics on files (CSV, Parquet)
- Need aggregations, GROUP BY, window functions
- Same-database queries
- Maximum performance needed

**When to use Streaming Engine:**

- Join different systems (DB + API + files)
- Need Python processing between joins
- Real-time/streaming data sources
- Simple joins only

### vs Apache Spark

| Feature                | Streaming SQL Engine            | Apache Spark                     |
| ---------------------- | ------------------------------- | -------------------------------- |
| **Setup**              | Zero-config                     | Requires cluster                 |
| **Scale**              | Single machine                  | Distributed clusters             |
| **Performance**        | Medium (Python)                 | Very fast (distributed)          |
| **Complexity**         | Simple                          | Complex                          |
| **Real-time**          | ✅ Native                       | ⚠️ Structured Streaming          |
| **Python integration** | ✅ Native                       | ⚠️ PySpark API                   |
| **Use case**           | Small-medium data, cross-system | Big data, distributed processing |

**When to use Spark:**

- Very large datasets (TB+)
- Need distributed processing
- Complex analytics workloads
- Have infrastructure/cluster

**When to use Streaming Engine:**

- Small-medium data (< 100M rows)
- No infrastructure available
- Cross-system joins
- Simple Python deployment

### vs Polars

| Feature            | Streaming SQL Engine | Polars               |
| ------------------ | -------------------- | -------------------- |
| **Language**       | Python               | Rust (Python API)    |
| **Performance**    | Slower               | Very fast            |
| **Query Language** | SQL                  | DataFrame API        |
| **Cross-system**   | ✅ Any source        | ⚠️ Limited           |
| **Real-time**      | ✅ Streaming         | ❌ Batch             |
| **SQL syntax**     | ✅ Standard SQL      | ❌ DataFrame methods |

**When to use Polars:**

- Fast data analysis
- DataFrame-style operations
- Python data science workflows
- Performance-critical analytics

**When to use Streaming Engine:**

- Need SQL syntax
- Cross-system joins
- Real-time processing
- API/file integration

### vs Direct Database Queries

| Feature                  | Streaming SQL Engine | Direct SQL      |
| ------------------------ | -------------------- | --------------- |
| **Same-database joins**  | Slower               | Much faster     |
| **Cross-database joins** | ✅ Possible          | ❌ Not possible |
| **API joins**            | ✅ Possible          | ❌ Not possible |
| **File joins**           | ✅ Possible          | ❌ Not possible |
| **Performance**          | Slower               | Faster          |
| **Flexibility**          | High                 | Low             |

**When to use Direct SQL:**

- All tables in same database
- Maximum performance needed
- Standard SQL features needed

**When to use Streaming Engine:**

- Different data sources
- Need Python processing
- Real-time sources

---

## Capabilities

### 1. **Cross-System Data Joins**

Join data from completely different sources in a single SQL query:

```python
# Join MySQL + PostgreSQL + API + CSV
engine.register("mysql_products", mysql_source)
engine.register("postgres_users", postgres_source)
engine.register("api_prices", api_source)
engine.register("csv_inventory", csv_source)

query = """
    SELECT p.name, u.email, a.price, i.quantity
    FROM mysql_products p
    JOIN postgres_users u ON p.user_id = u.id
    JOIN api_prices a ON p.sku = a.sku
    JOIN csv_inventory i ON p.sku = i.sku
"""
```

**Why this matters:**

- Modern applications use multiple data sources
- No need to export/import data
- Real-time joins across systems

---

### 2. **Streaming Row-by-Row Processing**

Process data as it arrives, never loading full tables:

```python
# Memory-efficient: only one row in memory at a time
for row in engine.query("SELECT * FROM huge_table JOIN ..."):
    process(row)  # Process and discard
    # Memory stays constant regardless of table size
```

**Benefits:**

- **Low memory usage**: Constant memory regardless of data size
- **Early results**: Start processing before all data arrives
- **Real-time**: Process data as it streams in

---

### 3. **Python-Native Integration**

Seamlessly integrate with Python ecosystem:

```python
# Use any Python library
def enriched_source():
    for row in db_source():
        row['sentiment'] = analyze_sentiment(row['text'])  # NLP
        row['score'] = ml_model.predict(row)  # ML
        row['processed'] = custom_python_function(row)  # Custom logic
        yield row

engine.register("enriched", enriched_source)
```

**Why this matters:**

- Access to entire Python ecosystem (ML, NLP, visualization)
- Easy to add custom processing
- No need to export/import data

---

### 4. **Zero-Configuration Deployment**

No infrastructure, clusters, or complex setup:

```python
# Just install and use
pip install streaming-sql-engine

# No config files, no clusters, no infrastructure
engine = Engine()
engine.register("table", source)
results = engine.query("SELECT * FROM table")
```

**Benefits:**

- **Easy deployment**: Works anywhere Python runs
- **No dependencies**: No external services needed
- **Simple**: Just Python code

---

### 5. **Standard SQL Syntax**

Use familiar SQL syntax for cross-system joins:

```python
# Standard SQL - no new syntax to learn
query = """
    SELECT
        p.name,
        c.category_name,
        u.email
    FROM products p
    JOIN categories c ON p.category_id = c.id
    JOIN users u ON p.user_id = u.id
    WHERE p.price > 100
"""
```

**Supported SQL:**

- ✅ SELECT (column selection, aliasing)
- ✅ FROM (table specification)
- ✅ JOIN (INNER, LEFT JOIN)
- ✅ WHERE (comparisons, AND/OR, NULL checks, IN clauses)
- ❌ GROUP BY, ORDER BY, aggregations (not supported)

---

### 6. **Flexible Data Source Registration**

Register any Python iterable as a data source:

```python
# Database
engine.register("db_table", create_table_source(pool, "table"))

# API
engine.register("api_data", lambda: fetch_from_api())

# File
engine.register("file_data", lambda: read_jsonl("data.jsonl"))

# Custom generator
def custom_source():
    for item in some_iterable:
        yield transform(item)
engine.register("custom", custom_source)

# All work the same way in SQL queries!
```

---

### 7. **Join Algorithm Selection**

Automatically chooses optimal join algorithm:

- **Lookup Join**: When right table is small (builds hash index)
- **Merge Join**: When both sides are sorted (efficient merge)

```python
# Automatically uses merge join if data is sorted
engine.register("table", source, ordered_by="id")
# Enables merge join optimization
```

---

### 8. **Type Coercion & Safety**

Handles type mismatches gracefully:

```python
# Automatically converts string numbers to numeric types
# CSV: "100" (string) vs JSONL: 100 (int)
# Engine handles the conversion automatically
query = "SELECT * FROM csv_data JOIN jsonl_data WHERE csv_data.price > jsonl_data.price"
```

**Safety features:**

- Type coercion for comparisons
- None value handling
- Invalid row filtering
- Error messages with context

---

## Why Use This Library

### Use Case 1: **Microservices Data Integration**

**Problem:** Data is spread across multiple microservices, each with its own database/API.

**Solution:**

```python
# Join data from multiple microservices
engine.register("orders_service", orders_api_source)
engine.register("users_service", users_api_source)
engine.register("products_service", products_db_source)

query = """
    SELECT o.order_id, u.name, p.name as product_name
    FROM orders_service o
    JOIN users_service u ON o.user_id = u.id
    JOIN products_service p ON o.product_id = p.id
"""
```

**Why this helps:**

- No need to replicate data
- Real-time joins across services
- No infrastructure changes needed

---

### Use Case 2: **Real-Time Data Enrichment**

**Problem:** Need to enrich database data with live API data.

**Solution:**

```python
# Join database with real-time API
engine.register("products", db_source)
engine.register("live_prices", lambda: fetch_latest_prices())

query = """
    SELECT p.name, lp.current_price, lp.currency
    FROM products p
    JOIN live_prices lp ON p.sku = lp.sku
"""
```

**Why this helps:**

- Real-time data without caching
- Always up-to-date joins
- No batch processing delays

---

### Use Case 3: **Data Pipeline with Python Processing**

**Problem:** Need to apply Python logic (ML, NLP) between joins.

**Solution:**

```python
def enriched_source():
    for row in db_source():
        row['sentiment'] = analyze_sentiment(row['text'])
        row['score'] = ml_model.predict(row)
        yield row

engine.register("enriched", enriched_source)
engine.register("categories", category_source)

query = "SELECT * FROM enriched JOIN categories WHERE enriched.score > 0.8"
```

**Why this helps:**

- Full Python ecosystem access
- Custom processing between joins
- No export/import needed

---

### Use Case 4: **Cross-Database Analytics**

**Problem:** Need to analyze data from multiple databases.

**Solution:**

```python
# Join MySQL + PostgreSQL
mysql_pool = create_mysql_pool_from_env()
pg_pool = create_postgresql_pool_from_env()

engine.register("mysql_data", create_table_source(mysql_pool, "table"))
engine.register("pg_data", create_table_source(pg_pool, "table"))

query = "SELECT * FROM mysql_data JOIN pg_data ON mysql_data.id = pg_data.id"
```

**Why this helps:**

- No database federation needed
- Works with any database
- Simple Python code

---

### Use Case 5: **File + Database Integration**

**Problem:** Need to join database data with file data (CSV, JSON).

**Solution:**

```python
engine.register("db_products", db_source)
engine.register("csv_inventory", lambda: read_csv("inventory.csv"))
engine.register("jsonl_prices", lambda: read_jsonl("prices.jsonl"))

query = """
    SELECT p.name, i.quantity, pr.price
    FROM db_products p
    JOIN csv_inventory i ON p.sku = i.sku
    JOIN jsonl_prices pr ON p.sku = pr.sku
"""
```

**Why this helps:**

- No need to import files to database
- Works with any file format
- Real-time file processing

---

## How to Use

### Installation

```bash
pip install streaming-sql-engine
```

Or from source:

```bash
git clone <repository>
cd sql_engine
pip install -e .
```

### Quick Start

```python
from streaming_sql_engine import Engine

# Create engine
engine = Engine()

# Register data sources
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

# Execute query
query = """
    SELECT users.name, departments.name AS dept_name
    FROM users
    JOIN departments ON users.dept_id = departments.id
    WHERE users.id > 1
"""

for row in engine.query(query):
    print(row)
# Output:
# {'name': 'Bob', 'dept_name': 'Sales'}
```

### Database Integration

```python
from streaming_sql_engine import Engine, create_mysql_pool_from_env, create_table_source

# Create connection pool
pool = create_mysql_pool_from_env()

# Create engine
engine = Engine()

# Register database tables
engine.register(
    "products",
    create_table_source(pool, "products", where_clause="is_active = 1")
)

engine.register(
    "categories",
    create_table_source(pool, "categories")
)

# Query
query = """
    SELECT p.name, c.category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
"""

for row in engine.query(query):
    print(row)
```

### API Integration

```python
import requests
from streaming_sql_engine import Engine

def api_source():
    response = requests.get("https://api.example.com/data")
    for item in response.json()["items"]:
        yield {
            "id": item["id"],
            "name": item["name"],
            "price": item["price"]
        }

engine = Engine()
engine.register("api_data", api_source)
engine.register("db_products", db_source)

query = """
    SELECT p.name, a.price
    FROM db_products p
    JOIN api_data a ON p.sku = a.sku
"""
```

### File Integration

```python
import json
import csv
from streaming_sql_engine import Engine

def jsonl_source(file_path):
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)

def csv_source(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

engine = Engine()
engine.register("jsonl_data", lambda: jsonl_source("data.jsonl"))
engine.register("csv_data", lambda: csv_source("data.csv"))

query = "SELECT * FROM jsonl_data JOIN csv_data ON jsonl_data.id = csv_data.id"
```

### Multi-Source Join Example

```python
# Join JSONL + CSV + API
engine.register("products", lambda: jsonl_source("products.jsonl"))
engine.register("categories", lambda: csv_source("categories.csv"))
engine.register("prices", api_price_source)

query = """
    SELECT
        p.name,
        c.category_name,
        pr.price
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN prices pr ON p.sku = pr.sku
    WHERE p.price > 50
"""

for row in engine.query(query):
    print(row)
```

### Advanced: Custom Processing

```python
def enriched_source():
    """Add Python processing to data."""
    for row in db_source():
        # Apply ML model
        row['prediction'] = ml_model.predict(row)

        # Apply NLP
        row['sentiment'] = analyze_sentiment(row['text'])

        # Custom logic
        row['score'] = calculate_score(row)

        yield row

engine.register("enriched", enriched_source)
engine.register("reference", reference_source)

query = "SELECT * FROM enriched JOIN reference WHERE enriched.score > 0.8"
```

---

## Technical Deep Dive

### Iterator Pipeline Execution

The engine builds a chain of iterators:

```python
# Example: SELECT * FROM users JOIN departments WHERE users.id > 1

# Step 1: Scan users table
scan = ScanIterator(users_source, "users", "u")
# Yields: {"u.id": 1, "u.name": "Alice", "u.dept_id": 10}

# Step 2: Filter WHERE users.id > 1
filtered = FilterIterator(scan, where_expr)
# Evaluates: 1 > 1 → False, skip row
# Evaluates: 2 > 1 → True, keep row

# Step 3: Join with departments
joined = LookupJoinIterator(filtered, dept_source, "u.dept_id", "d.id")
# Builds index: {10: [{"d.id": 10, "d.name": "Engineering"}], ...}
# For row with dept_id=20, looks up: index[20] = [{"d.id": 20, "d.name": "Sales"}]
# Merges: {"u.id": 2, "u.name": "Bob", "u.dept_id": 20, "d.id": 20, "d.name": "Sales"}

# Step 4: Project SELECT columns
projected = ProjectIterator(joined, projections)
# Extracts only requested columns
```

### Memory Management

**Lookup Join:**

- Builds hash index from right table: O(n) memory
- Left table: O(1) memory (one row at a time)
- **Total**: O(n) where n = size of right table

**Merge Join:**

- Both sides: O(1) memory (one row at a time)
- **Total**: O(1) memory (constant)

**Best Practice:**

- Put smaller table on right side (for lookup join)
- Use merge join when both sides are sorted

### Performance Characteristics

**Time Complexity:**

- **Lookup Join**: O(n + m) where n = left size, m = right size
- **Merge Join**: O(n + m) but faster in practice (better cache locality)
- **Filter**: O(n) where n = number of rows
- **Project**: O(n) where n = number of rows

**Bottlenecks:**

1. **Python overhead**: Interpreted language, slower than C++
2. **Dictionary operations**: Hash lookups, merging
3. **Expression evaluation**: Recursive AST traversal
4. **I/O**: Database/API/File reads

**Optimizations Applied:**

- Type caching for faster isinstance() checks
- Dictionary comprehensions for column prefixing
- Short-circuit evaluation for AND/OR
- Type coercion for comparisons

---

## Summary

The **Streaming SQL Join Engine** is a Python-native solution for joining data across different systems. It combines:

- **Database query execution principles** (Volcano model, join algorithms)
- **Python iterator protocol** (lazy evaluation, composability)
- **Streaming processing concepts** (row-by-row, incremental)
- **Functional programming patterns** (immutable data, pure functions)

**Key Differentiators:**

1. ✅ Cross-system joins (DB + API + Files)
2. ✅ Zero-configuration (no infrastructure)
3. ✅ Python-native (full ecosystem access)
4. ✅ Real-time capable (streaming sources)
5. ✅ Simple deployment (just Python)

**Best For:**

- Microservices data integration
- Real-time data enrichment
- Cross-database analytics
- File + database joins
- Python processing pipelines

**Not Best For:**

- Same-database queries (use direct SQL)
- Big data analytics (use Spark)
- Complex aggregations (use DuckDB)
- Maximum performance (use C++ engines)

---

## References & Inspiration

### Academic Papers

- Graefe, G. (1993). "The Volcano Optimizer Generator: Extensibility and Efficient Search"
- Graefe, G. (1990). "Encapsulation of Parallelism in the Volcano Query Processing System"

### Database Systems

- PostgreSQL query executor architecture
- SQLite query execution model
- MySQL join algorithms

### Streaming Systems

- Apache Flink streaming architecture
- Kafka Streams processing model

### Python Patterns

- Python iterator protocol (PEP 234)
- Generator functions and lazy evaluation
- Functional programming in Python

---

## License & Credits

This implementation demonstrates core database query execution concepts in pure Python, making them accessible for cross-system data integration scenarios where traditional databases fall short.
