# Join Data from Anywhere: The Streaming SQL Engine That Bridges Databases, APIs, and Files

---

Have you ever needed to join data from a MySQL database with a PostgreSQL database, a MongoDB collection, and a REST API — all in one query? Traditional databases can't do this. That's why I built the Streaming SQL Engine.\_

---

## The Problem: Data Lives Everywhere

Modern applications don't store all their data in one place. You might have:

- User data in PostgreSQL
- Order data in MySQL
- Product catalog in MongoDB
- Pricing information from a REST API
- Inventory data in CSV files
- Product feeds in XML files

**The challenge:** How do you join all this data together?

Traditional solutions require:

- Exporting data from each system
- Importing into a central database
- Writing complex ETL pipelines
- Maintaining data synchronization

**There had to be a better way.**

---

## The Solution: Streaming SQL Engine

I built a lightweight Python library that lets you join data from **any source** using standard SQL syntax — without exporting, importing, or setting up infrastructure.

```python
from streaming_sql_engine import Engine
import psycopg2
import pymysql
from pymongo import MongoClient
import requests
import csv

engine = Engine()

# Register PostgreSQL source (iterator function)
def postgres_users():
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()
engine.register("postgres_users", postgres_users)

# Register MySQL source (iterator function)
def mysql_products():
    conn = pymysql.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "price": row[2]}
    conn.close()
engine.register("mysql_products", mysql_products)

# Register MongoDB source (iterator function)
def mongo_inventory():
    client = MongoClient("mongodb://localhost:27017")
    for doc in client.mydb.inventory.find():
        yield doc
engine.register("mongo_inventory", mongo_inventory)

# Register REST API source (iterator function)
def api_prices():
    response = requests.get("https://api.example.com/prices")
    for item in response.json():
        yield item
engine.register("api_prices", api_prices)

# Register CSV source (iterator function)
def csv_suppliers():
    with open("suppliers.csv") as f:
        for row in csv.DictReader(f):
            yield row
engine.register("csv_suppliers", csv_suppliers)

# Join them all in one SQL query!
query = """
    SELECT
        mysql_products.name,
        postgres_users.email,
        mongo_inventory.quantity,
        api_prices.price,
        csv_suppliers.supplier_name
    FROM mysql_products
    JOIN postgres_users ON mysql_products.user_id = postgres_users.id
    JOIN mongo_inventory ON mysql_products.sku = mongo_inventory.sku
    JOIN api_prices ON mysql_products.sku = api_prices.sku
    JOIN csv_suppliers ON mysql_products.supplier_id = csv_suppliers.id
    WHERE api_prices.price > 100
"""

for row in engine.query(query):
    process(row)
```

**That's it.** No clusters, no infrastructure, no data export — just pure Python and SQL.

---

## Why I Built This: The Problem That Needed Solving

I was working on a data reconciliation project where I needed to join data from multiple sources:

- MySQL database (product catalog)
- PostgreSQL database (user data)
- MongoDB collection (inventory)
- REST API (pricing information)
- CSV files (supplier data)

**The challenge:** Traditional databases can't join across different systems. I had three options:

1. **Export everything to one database** - Time-consuming, requires ETL pipelines, data becomes stale
2. **Write custom Python code** - Complex, error-prone, hard to maintain
3. **Use existing tools** - Spark/Flink require clusters, DuckDB requires data import, Presto needs infrastructure

**None of these worked for my use case.** I needed something that:

- Could join data from different systems without export
- Was simple to use (SQL syntax)
- Required zero infrastructure
- Worked with Python natively
- Processed data efficiently (streaming)

So I built the Streaming SQL Engine.

---

## How I Built It: Architecture and Design Decisions

### Core Design Philosophy

The engine follows a **pipeline architecture** inspired by database query execution engines (like PostgreSQL and SQLite), but implemented in pure Python using iterators.

**Key insight:** Python's iterator protocol is perfect for streaming data. Each operator in the pipeline is an iterator that processes rows one at a time.

### Why Iterator-Based Architecture?

**Key advantages:**

1. **Memory efficiency:** Only one row in memory at a time (except for join indexes)
2. **Lazy evaluation:** Processing starts only when you iterate over results
3. **Composability:** Operators can be chained arbitrarily
4. **Extensibility:** Easy to add new operators
5. **Python-native:** Uses standard Python iterator protocol

**Trade-offs:**

- **Performance:** Python iterators are slower than compiled code, but flexibility is worth it
- **Memory:** Join indexes require memory, but this is necessary for efficient joins
- **Complexity:** Iterator chains can be complex, but they're composable and testable

### Expression Evaluation

**How WHERE clauses are evaluated:**

The engine uses recursive AST traversal to evaluate expressions:

**Why recursive:** SQL expressions are trees. Recursive evaluation naturally handles nested expressions like `(a > 10 AND b < 20) OR c = 5`.

### Join Algorithm Selection

**How the engine chooses join algorithms:**

The engine follows this priority order when selecting a join algorithm:

1. **Check if both sides are sorted** (`ordered_by` metadata)

   - If yes, use `MergeJoinIterator` (most memory-efficient for sorted data)
   - Only used when `use_polars=False`

2. **Check if right side is a file** (`filename` metadata)

   - If yes, use `MmapLookupJoinIterator` (memory-mapped, 90-99% memory reduction)
   - Only used when `use_polars=False`

3. **Check if Polars is available** (`use_polars` flag)

   - If yes, use `PolarsLookupJoinIterator` (vectorized, SIMD-accelerated)
   - Used when `use_polars=True` is explicitly set

4. **Default fallback**
   - Use `LookupJoinIterator` (Python hash-based, most compatible)

**Logic:**

**Note:** When `use_polars=False` (default), Merge Join and MMAP Join are checked first before falling back to Python Lookup Join. When `use_polars=True` is explicitly set, the engine prioritizes Polars over MMAP and Merge Join.

### Protocol-Based Optimization

**The key innovation:** Automatic optimization detection via function signature inspection.

**How it works:**

1. Engine inspects source function signature using `inspect.signature()`
2. If function accepts `dynamic_where` or `dynamic_columns` parameters, it supports optimizations
3. Engine passes optimization parameters automatically
4. Source function applies optimizations (filter pushdown, column pruning)

**Why this approach:**

- **No flags needed:** Detection is automatic
- **Flexible:** Any Python function can be a source
- **Backward compatible:** Simple sources still work (no optimizations)
- **Extensible:** Easy to add new optimization parameters

**Example:**

```python
# Simple source (no optimizations)
def simple_source():
    return iter([{"id": 1, "name": "Alice"}])

# Optimized source (with protocol)
def optimized_source(dynamic_where=None, dynamic_columns=None):
    query = "SELECT "
    if dynamic_columns:
        query += ", ".join(dynamic_columns)
    else:
        query += "*"
    query += " FROM table"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"
    return execute_query(query)

# Both work the same way:
engine.register("users", simple_source)  # No optimizations
engine.register("products", optimized_source)  # Optimizations apply automatically!
```

### Memory Management

**Key strategies:**

1. **Streaming:** Process one row at a time, never load full tables
2. **Join indexes:** Only right side of joins is materialized (necessary for lookups)
3. **Memory-mapped files:** For large JSONL files, use OS virtual memory
4. **Column pruning:** Only extract needed columns
5. **Filter pushdown:** Filter at source, reduce data transfer

**Memory footprint:**

- **Left side of join:** O(1) - one row at a time
- **Right side of join:** O(n) - hash index in memory
- **Total:** O(n) where n = size of right side

**Why this works:** In most queries, the right side is smaller (e.g., joining large product table with small category table). The engine is designed to put smaller tables on the right side.

### Performance Optimizations

**1. Polars Vectorization**

When Polars is available, the engine uses vectorized operations:

```python
# Instead of row-by-row filtering:
for row in rows:
    if row['price'] > 100:
        yield row

# Use Polars batch filtering:
df = pl.DataFrame(rows)
filtered_df = df.filter(pl.col('price') > 100)
for row in filtered_df.iter_rows(named=True):
    yield row
```

**Why faster:** Polars uses SIMD instructions and columnar processing, 10-200x faster than row-by-row Python loops.

**2. Memory-Mapped Joins**

For large JSONL files, use OS virtual memory instead of loading into RAM:

```python
# Instead of loading entire file:
with open('large_file.jsonl') as f:
    data = [json.loads(line) for line in f]  # 10GB in memory!

# Use memory-mapped file:
import mmap
with open('large_file.jsonl', 'rb') as f:
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    # OS handles memory, can process files larger than RAM
```

**Why this works:** OS virtual memory allows accessing file data without loading it all into RAM. 90-99% memory reduction for large files.

**3. First Match Only Optimization**

For joins where only the first match matters (prevents Cartesian products).

**Why useful:** Prevents Cartesian products when right side has duplicate keys. Significantly reduces output size and processing time.

### Design Decisions and Trade-offs

**1. Why Python iterators instead of compiled code?**

**Decision:** Use Python iterators for flexibility

**Trade-off:** Slower than compiled code, but:

- Works with any Python data source
- Easy to extend and customize
- No compilation step needed
- Python-native integration

**2. Why separate logical planning from execution?**

**Decision:** Two-phase approach (plan then execute)

**Trade-off:** Extra step, but:

- Enables query optimization
- Easier to test and debug
- Can reuse planning logic
- Clear separation of concerns

**3. Why protocol-based optimization instead of flags?**

**Decision:** Automatic detection via function signature

**Trade-off:** Slightly more complex detection, but:

- No flags to remember
- Automatic optimization
- Backward compatible
- More Pythonic

**4. Why materialize right side of joins?**

**Decision:** Build hash index on right side

**Trade-off:** Memory usage, but:

- O(1) lookup time per left row
- Necessary for efficient joins
- Can use memory-mapped files for large files
- Standard database approach

**5. Why limit SQL features (no GROUP BY, aggregations)?**

**Decision:** Focus on joins and filtering

**Trade-off:** Less SQL support, but:

- Simpler implementation
- Faster execution
- Focuses on core use case (cross-system joins)
- Can add later if needed

### The Result

A lightweight Python library that:

- Joins data from any source using SQL
- Processes data row-by-row (streaming)
- Requires zero infrastructure
- Automatically optimizes when possible
- Works with any Python iterator

**The key insight:** Python's iterator protocol is perfect for streaming SQL execution. By combining SQL parsing, logical planning, and iterator-based execution, I created a tool that solves a real problem: joining data from different systems without complex infrastructure.

---

## Real-World Performance: 39 Million Records in 7 Minutes

I recently used this engine in production to compare prices between two XML files (17 million records each) and match them with a MongoDB collection (5 million records).

**The results:**

- **39 million total records processed**
- **7 minutes execution time**
- **400 MB memory usage**
- **92,857 records/second throughput**

This demonstrates the engine's efficiency: processing massive datasets with minimal memory footprint through true streaming architecture.

---

## How It Works: Streaming Architecture

The engine processes data **row-by-row**, never loading entire tables into memory:

```
SQL Query
    |
Parser -> AST
    |
Planner -> Logical Plan
    |
Executor -> Iterator Pipeline
    |
Results (Generator)
```

**Iterator Pipeline:**

```
ScanIterator -> FilterIterator -> JoinIterators -> ProjectIterator -> Results
```

Each iterator processes rows incrementally, enabling true streaming execution. This means:

- Low memory footprint
- Can process data larger than RAM
- Results yielded immediately
- No buffering required

---

## Supported Data Sources

The engine works with **any Python iterator**, making it incredibly flexible:

### Databases

All databases are accessed via Python iterator functions. The engine doesn't use connectors - it works with any Python function that returns an iterator:

- **PostgreSQL** - Create iterator function that queries PostgreSQL and yields rows
- **MySQL** - Create iterator function that queries MySQL and yields rows
- **MongoDB** - Create iterator function that queries MongoDB and yields documents

### Files

- **CSV** - Standard CSV files
- **JSONL** - JSON Lines format with memory-mapped joins
- **JSON** - Standard JSON files
- **XML** - XML parsing with ElementTree

### APIs

- **REST APIs** - Any HTTP endpoint
- **GraphQL** - Via custom functions
- **WebSockets** - Streaming data sources

### Custom Sources

- **Any Python function** that returns an iterator
- **Generators** - Perfect for streaming data
- **Custom transformations** - Apply Python logic between joins

---

## SQL Features

The engine supports standard SQL syntax:

### Supported Features

**SELECT** - Column selection, aliasing, table-qualified columns

```sql
SELECT users.name, orders.total AS order_total
FROM users
JOIN orders ON users.id = orders.user_id
```

**JOIN** - INNER JOIN and LEFT JOIN with equality conditions

```sql
SELECT *
FROM table1 t1
JOIN table2 t2 ON t1.id = t2.id
LEFT JOIN table3 t3 ON t1.id = t3.id
```

**WHERE** - Comparisons, boolean logic, NULL checks, IN clauses

```sql
SELECT *
FROM products
WHERE price > 100
  AND status IN ('active', 'pending')
  AND description IS NOT NULL
```

**Arithmetic** - Addition, subtraction, multiplication, division, modulo

```sql
SELECT
  price - discount AS final_price,
  quantity * unit_price AS total
FROM orders
```

### Not Supported

- GROUP BY and aggregations (COUNT, SUM, AVG)
- ORDER BY
- HAVING
- Subqueries

_These limitations keep the engine focused on joins and filtering — its core strength._

---

## Performance Optimizations

The engine includes several automatic optimizations:

### 1. Column Pruning

Only extracts columns needed for the query, reducing I/O and memory:

```python
# Query only requests 'name' and 'price'
query = "SELECT name, price FROM products"

# Engine automatically requests only these columns from source
def source(dynamic_columns=None):
    columns = ", ".join(dynamic_columns)  # ['name', 'price']
    query = f"SELECT {columns} FROM table"
```

### 2. Filter Pushdown

Pushes WHERE conditions to data sources when possible:

```python
# Query has WHERE clause
query = "SELECT * FROM products WHERE price > 100"

# Engine automatically pushes filter to source
def source(dynamic_where=None):
    query = f"SELECT * FROM table WHERE {dynamic_where}"
```

### 3. Polars Vectorization

10-200x faster processing for large datasets using SIMD-accelerated operations:

```python
engine = Engine()  # use_polars=False (default)

# Automatically uses Polars when available for:
# - Vectorized joins (PolarsLookupJoinIterator) - when right side >= 10K rows
# - Vectorized filtering (PolarsBatchFilterIterator) - when expression is translatable
# - Vectorized projections (PolarsBatchProjectIterator) - batch column selection
# Falls back to Python iterators if Polars fails or isn't available
```

### 4. Memory-Mapped Joins

90-99% memory reduction for large JSONL files:

```python
# Register with filename to enable mmap joins
engine.register("products", jsonl_source, filename="products.jsonl")

# Engine uses OS virtual memory instead of RAM
# Can process files larger than available RAM
```

### 5. Merge Joins

Efficient joins for pre-sorted data (O(n+m) time complexity):

```python
# Register with ordered_by to enable merge join
engine.register("users", users_source, ordered_by="id")

# Engine uses merge join algorithm
# Both sides must be sorted by join key
```

---

## Real-World Examples

### Example 1: Microservices Data Integration

In a microservices architecture, data is distributed across services:

```python
from streaming_sql_engine import Engine
import psycopg2
import pymysql
import requests

engine = Engine()

# Service 1: User service (PostgreSQL) - iterator function
def users_source():
    conn = psycopg2.connect(host="user-db", port=5432, user="user", password="pass", database="users_db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()
engine.register("users", users_source)

# Service 2: Order service (MySQL) - iterator function
def orders_source():
    conn = pymysql.connect(host="order-db", port=3306, user="user", password="pass", database="orders_db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, total FROM orders")
    for row in cursor:
        yield {"id": row[0], "user_id": row[1], "total": row[2]}
    conn.close()
engine.register("orders", orders_source)

# Service 3: Payment service (REST API) - iterator function
def payment_source():
    response = requests.get("https://payments.service/api/transactions")
    for item in response.json():
        yield item
engine.register("payments", payment_source)

# Join across services
query = """
    SELECT users.name, orders.total, payments.status
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN payments ON orders.id = payments.order_id
"""
```

**Why this matters:** No need for a shared database or complex ETL pipelines. The engine accepts any Python function that returns an iterator, making it incredibly flexible.

### Example 2: Real-Time Price Comparison

Compare prices from multiple XML feeds and match with MongoDB:

```python
def parse_xml(filepath):
    tree = ET.parse(filepath)
    for product in tree.findall('.//product'):
        yield {
            'ean': product.find('ean').text,
            'price': float(product.find('price').text),
            'name': product.find('name').text
        }

engine.register("xml1", lambda: parse_xml("prices1.xml"))
engine.register("xml2", lambda: parse_xml("prices2.xml"))
engine.register("mongo", mongo_source)

query = """
    SELECT
        xml1.ean,
        xml1.price AS price1,
        xml2.price AS price2,
        mongo.sf_sku
    FROM xml1
    JOIN xml2 ON xml1.ean = xml2.ean
    JOIN mongo ON xml1.ean = mongo.ean
    WHERE xml1.price != xml2.price
"""
```

**Production results:** 17M + 17M XML records + 5M MongoDB records processed in 7 minutes using 400 MB RAM.

### Example 3: Python Processing Between Joins

Apply Python logic (ML models, custom functions) between joins:

```python
def enriched_source():
    """Source that processes data with Python before joining"""
    import psycopg2
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category_id FROM products")
    for row in cursor:
        product = {"id": row[0], "name": row[1], "category_id": row[2]}
        # Apply Python logic
        product['ml_score'] = ml_model.predict(product)
        product['custom_field'] = custom_function(product)
        yield product
    conn.close()

def categories_source():
    import psycopg2
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories")
    for row in cursor:
        yield {"id": row[0], "category_name": row[1]}
    conn.close()

engine.register("enriched_products", enriched_source)
engine.register("categories", categories_source)

query = """
    SELECT p.name, p.ml_score, c.category_name
    FROM enriched_products p
    JOIN categories c ON p.category_id = c.id
"""
```

**Why this matters:** Seamless integration with Python ecosystem — use any library, apply any logic.

---

## Comparison with Alternatives

### vs DuckDB

| Feature                 | Streaming SQL Engine | DuckDB              |
| ----------------------- | -------------------- | ------------------- |
| Cross-system joins      | ✅ Direct            | ⚠️ Requires import  |
| API + Database join     | ✅ Direct            | ❌ Must export API  |
| Real-time streaming     | ✅ True streaming    | ⚠️ Buffering needed |
| Python processing       | ✅ Native            | ⚠️ Export/import    |
| GROUP BY / Aggregations | ❌ Not supported     | ✅ Full support     |
| Performance (same DB)   | ⚠️ Moderate          | ✅ Very fast        |

**Use Streaming SQL Engine when:** You need to join data from different systems that can't be imported into DuckDB.

**Use DuckDB when:** All data can be imported and you need aggregations.

### vs PySpark

| Feature                | Streaming SQL Engine | PySpark            |
| ---------------------- | -------------------- | ------------------ |
| Infrastructure         | ✅ Zero              | ❌ Cluster needed  |
| Setup time             | ✅ Seconds           | ❌ Hours           |
| Memory (small queries) | ✅ 100-500 MB        | ❌ 4-8 GB minimum  |
| Cross-system joins     | ✅ Direct            | ⚠️ Requires import |
| Distributed processing | ❌ Single machine    | ✅ Multi-machine   |
| Big data (petabytes)   | ❌ Not suitable      | ✅ Excellent       |
| Python integration     | ✅ Native Python     | ⚠️ PySpark API     |
| Learning curve         | ✅ Simple            | ❌ Steeper         |

**Use Streaming SQL Engine when:** You need cross-system joins on a single machine with simple deployment.

**Use PySpark when:** You need distributed processing across multiple machines for petabyte-scale data.

### vs Apache Flink

| Feature                | Streaming SQL Engine | Apache Flink           |
| ---------------------- | -------------------- | ---------------------- |
| Infrastructure         | ✅ Zero              | ❌ Cluster needed      |
| Setup complexity       | ✅ Very low          | ❌ High                |
| Python-native          | ✅ Pure Python       | ⚠️ Python API wrapper  |
| Cross-system joins     | ✅ Direct            | ⚠️ Requires connectors |
| Real-time streaming    | ✅ True streaming    | ✅ Excellent           |
| Distributed processing | ❌ Single machine    | ✅ Multi-machine       |
| Fault tolerance        | ❌ Not provided      | ✅ Built-in            |
| Exactly-once semantics | ❌ Not provided      | ✅ Supported           |
| Event-time processing  | ❌ Not supported     | ✅ Full support        |
| Low latency            | ✅ Immediate         | ⚠️ Network overhead    |

**Use Streaming SQL Engine when:** You need simple cross-system joins, Python-native workflows, and zero infrastructure.

**Use Apache Flink when:** You need distributed stream processing, fault tolerance, exactly-once semantics, and complex event-time processing.

### vs Pandas

| Feature                  | Streaming SQL Engine   | Pandas                   |
| ------------------------ | ---------------------- | ------------------------ |
| Cross-system joins       | ✅ Direct              | ❌ Must load all data    |
| Memory efficiency        | ✅ Streaming           | ❌ Loads all in memory   |
| SQL syntax               | ✅ Standard SQL        | ❌ DataFrame API         |
| Large datasets           | ✅ Can exceed RAM      | ❌ Limited by RAM        |
| Real-time data           | ✅ Streaming           | ❌ Batch only            |
| File formats             | ✅ Any Python iterator | ⚠️ Limited formats       |
| Performance (large data) | ✅ Streaming           | ⚠️ Slower for large data |

**Use Streaming SQL Engine when:** You need to join data from different systems, process data larger than RAM, or use SQL syntax.

**Use Pandas when:** All data fits in memory and you prefer DataFrame API.

### vs SQLAlchemy

| Feature               | Streaming SQL Engine | SQLAlchemy                |
| --------------------- | -------------------- | ------------------------- |
| Cross-database joins  | ✅ Direct            | ❌ One database at a time |
| API joins             | ✅ Direct            | ❌ Not supported          |
| File joins            | ✅ Direct            | ❌ Not supported          |
| SQL syntax            | ✅ Standard SQL      | ✅ ORM or SQL             |
| Same-database queries | ⚠️ Slower            | ✅ Optimized              |
| Database abstraction  | ❌ Not provided      | ✅ Full ORM               |

**Use Streaming SQL Engine when:** You need to join data from different systems (databases, APIs, files).

**Use SQLAlchemy when:** All data is in the same database and you want ORM features.

### vs Presto/Trino

| Feature            | Streaming SQL Engine | Presto/Trino                  |
| ------------------ | -------------------- | ----------------------------- |
| Infrastructure     | ✅ Zero              | ❌ Cluster needed             |
| Setup complexity   | ✅ Very low          | ❌ High                       |
| Cross-system joins | ✅ Direct            | ✅ Supported                  |
| Python integration | ✅ Native            | ⚠️ JDBC/ODBC                  |
| Real-time APIs     | ✅ Direct            | ⚠️ Requires connector         |
| Memory efficiency  | ✅ Streaming         | ⚠️ Query coordinator overhead |
| SQL features       | ⚠️ Limited           | ✅ Full SQL                   |
| Aggregations       | ❌ Not supported     | ✅ Full support               |

**Use Streaming SQL Engine when:** You need Python-native cross-system joins with zero infrastructure.

**Use Presto/Trino when:** You need full SQL features, aggregations, and have infrastructure for a cluster.

### vs Apache Drill

| Feature            | Streaming SQL Engine | Apache Drill          |
| ------------------ | -------------------- | --------------------- |
| Infrastructure     | ✅ Zero              | ❌ Cluster needed     |
| Language           | ✅ Python            | ❌ Java               |
| Deployment         | ✅ pip install       | ❌ Server setup       |
| Cross-system joins | ✅ Direct            | ✅ Supported          |
| API joins          | ✅ Direct            | ⚠️ Requires connector |
| Python integration | ✅ Native            | ⚠️ JDBC/ODBC          |
| SQL features       | ⚠️ Limited           | ✅ Full SQL           |
| Scalability        | ❌ Single machine    | ✅ 1000+ nodes        |

**Use Streaming SQL Engine when:** You need simple Python-native cross-system joins with zero setup.

**Use Apache Drill when:** You need enterprise-scale distributed querying across Hadoop/NoSQL systems.

### vs ksqlDB

| Feature            | Streaming SQL Engine | ksqlDB                  |
| ------------------ | -------------------- | ----------------------- |
| Infrastructure     | ✅ Zero              | ❌ Kafka cluster needed |
| Data sources       | ✅ Any Python source | ⚠️ Kafka topics only    |
| API joins          | ✅ Direct            | ❌ Not supported        |
| File joins         | ✅ Direct            | ⚠️ Requires Kafka       |
| Python integration | ✅ Native            | ⚠️ REST API             |
| Real-time          | ✅ Streaming         | ✅ Excellent            |
| SQL features       | ⚠️ Limited           | ✅ Full SQL             |

**Use Streaming SQL Engine when:** You need to join data from databases, APIs, and files without Kafka.

**Use ksqlDB when:** You're already using Kafka and need streaming SQL on Kafka topics.

### vs Materialize

| Feature            | Streaming SQL Engine | Materialize              |
| ------------------ | -------------------- | ------------------------ |
| Infrastructure     | ✅ Zero              | ❌ Database server       |
| Deployment         | ✅ Python library    | ❌ Database installation |
| Cross-system joins | ✅ Direct            | ⚠️ Requires connectors   |
| Materialized views | ❌ Not supported     | ✅ Core feature          |
| Python integration | ✅ Native            | ⚠️ SQL/psql              |
| Real-time          | ✅ Streaming         | ✅ Excellent             |
| SQL features       | ⚠️ Limited           | ✅ Full SQL              |

**Use Streaming SQL Engine when:** You need simple Python-native joins without database infrastructure.

**Use Materialize when:** You need materialized views over streaming data with full SQL support.

### vs DataFusion (Apache Arrow)

| Feature            | Streaming SQL Engine | DataFusion               |
| ------------------ | -------------------- | ------------------------ |
| Language           | ✅ Python            | ⚠️ Rust (Python wrapper) |
| Infrastructure     | ✅ Zero              | ✅ Zero                  |
| Cross-system joins | ✅ Direct            | ⚠️ Limited connectors    |
| API joins          | ✅ Direct            | ❌ Not supported         |
| Python integration | ✅ Native            | ⚠️ Python wrapper        |
| Performance        | ⚠️ Moderate          | ✅ Very fast (Rust)      |
| SQL features       | ⚠️ Limited           | ✅ Full SQL              |

**Use Streaming SQL Engine when:** You need to join APIs and files with Python-native flexibility.

**Use DataFusion when:** You need high-performance SQL queries on Arrow/Parquet data.

### vs Polars SQL

| Feature            | Streaming SQL Engine | Polars SQL               |
| ------------------ | -------------------- | ------------------------ |
| Data sources       | ✅ Any Python source | ⚠️ DataFrames/Parquet    |
| Cross-system joins | ✅ Direct            | ⚠️ Must load into Polars |
| API joins          | ✅ Direct            | ❌ Not supported         |
| Memory efficiency  | ✅ Streaming         | ⚠️ Loads into memory     |
| SQL syntax         | ✅ Standard SQL      | ✅ Standard SQL          |
| Python integration | ✅ Native            | ✅ Native                |
| Performance        | ⚠️ Moderate          | ✅ Very fast             |

**Use Streaming SQL Engine when:** You need to join data from different systems without loading into Polars.

**Use Polars SQL when:** All data can be loaded into Polars DataFrames and you need high performance.

---

## Are There Other Tools Like This?

**Short answer: Not exactly.**

While there are many tools that do **parts** of what Streaming SQL Engine does, none combine all these characteristics:

### What Makes Streaming SQL Engine Unique

1. **Zero Infrastructure + Cross-System Joins**

   - Most tools require clusters (Spark, Flink, Drill)
   - Or require specific infrastructure (ksqlDB needs Kafka)
   - Streaming SQL Engine: Just Python

2. **Any Python Iterator as Data Source**

   - Most tools require specific connectors
   - Streaming SQL Engine: Any Python function works

3. **Direct API Joins**

   - Most tools can't join REST APIs directly
   - Streaming SQL Engine: Native support

4. **Python-Native Architecture**
   - Most tools are Java/Rust with Python wrappers
   - Streaming SQL Engine: Pure Python, seamless integration

### Similar Tools (But Different)

**Apache Drill** — Similar cross-system capability, but requires cluster and Java

**ksqlDB** — Streaming SQL, but Kafka-only and requires infrastructure

**Materialize** — Streaming database, but requires database server

**DataFusion** — Fast SQL engine, but limited to Arrow/Parquet data

**Polars SQL** — Fast SQL, but requires loading data into DataFrames first

**Presto/Trino** — Cross-system SQL, but requires cluster infrastructure

**None of these** combine:

- Zero infrastructure
- Any Python iterator as source
- Direct API joins
- Pure Python implementation
- Simple deployment

**That's what makes Streaming SQL Engine unique.**

---

## Key Wins

### 1. Cross-System Joins

The **only tool** that can join MySQL + PostgreSQL + MongoDB + REST API + CSV files in a single SQL query without data export/import.

### 2. Zero Infrastructure

No clusters, no setup, just Python. Install and use immediately:

```bash
pip install streaming-sql-engine
```

### 3. Memory Efficient

Processes 39 million records with only 400 MB RAM. True streaming architecture means you can process data larger than available RAM.

### 4. Python-Native

Seamless integration with Python ecosystem. Use any Python function as a data source, apply ML models, use any library.

### 5. Real-Time Processing

Join live streaming data with static reference data. No buffering required — true streaming execution.

### 6. Automatic Optimizations

Filter pushdown, column pruning, and vectorization applied automatically. No configuration needed — the engine detects protocol support.

---

## When to Use Streaming SQL Engine

**Perfect for:**

- Joining data from different systems (databases, APIs, files)
- Microservices data aggregation
- Real-time data integration
- Memory-constrained environments
- Python-native workflows
- Ad-hoc cross-system queries

**Not for:**

- All data in same database (use direct SQL - 10-100x faster)
- Need GROUP BY or aggregations (use database)
- Maximum performance for same-database queries (use database)
- Distributed processing (use Spark/Flink)

---

## 🎯 Start Here: The Most Secure Way

### Step 1: Install and Basic Setup

```bash
pip install streaming-sql-engine
```

### Step 2: Use the Default Configuration (Most Stable)

**This is the safest way to start** — it handles all edge cases, works with any data types, and requires no special configuration:

```python
from streaming_sql_engine import Engine

# Default configuration: Most stable and reliable
engine = Engine()  # use_polars=False (default)

# Register your data sources
def postgres_users():
    # Your PostgreSQL connection code
    for row in cursor:
        yield {"id": row[0], "name": row[1]}

def mysql_orders():
    # Your MySQL connection code
    for row in cursor:
        yield {"id": row[0], "user_id": row[1], "total": row[2]}

engine.register("users", postgres_users)
engine.register("orders", mysql_orders)

# Write SQL queries
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
    WHERE orders.total > 100
"""

# Execute and iterate results
for row in engine.query(query):
    print(row)
```

**Why This Configuration is Best to Start:**

- **Most Stable**: Handles mixed data types gracefully
- **No Schema Errors**: No type inference issues
- **Works Everywhere**: No external dependencies required
- **Reliable**: Battle-tested Python code
- **Fast for Small-Medium Data**: 0.72s for 10K rows

**Use this when:**

- You're just getting started
- Your datasets are < 100K rows
- You have mixed data types
- You need maximum reliability
- Polars is not available

---

## Experimenting with Options

Once you're comfortable with the basics, you can experiment with different options to optimize for your specific use case.

### Option 1: Enable Debug Mode

See what's happening under the hood:

```python
engine = Engine(debug=True)  # Shows execution details
```

**Output:**

```
============================================================
STREAMING SQL ENGINE - DEBUG MODE
============================================================

[1/3] PARSING SQL QUERY...
SQL parsed successfully

[2/3] BUILDING LOGICAL PLAN...
Logical plan built

[3/3] EXECUTING QUERY...
  Using LOOKUP JOIN (building index...)
```

---

### Option 2: Enable Polars (For Large Datasets)

**When to use**: Large datasets (> 100K rows), consistent data types

```python
engine = Engine(use_polars=True)  # Enable Polars for speed
```

**Benefits:**

- Faster for large datasets (vectorized operations)
- SIMD acceleration
- Better for consistent schemas

**Trade-offs:**

- Requires data normalization (consistent types)
- Can fail on mixed types
- Requires Polars dependency

**Example:**

```python
engine = Engine(use_polars=True)

# Make sure your data has consistent types
def normalized_source():
    for row in raw_source():
        yield {
            "id": int(row.get("id", 0)),
            "price": float(row.get("price", 0.0)),
            "name": str(row.get("name", "")),
        }

engine.register("products", normalized_source)
```

---

### Option 3: Enable MMAP (For Large Files)

**When to use**: Large files (> 100MB), memory-constrained systems

```python
engine = Engine()
engine.register("products", source, filename="products.jsonl")  # MMAP enabled
```

**Benefits:**

- 90-99% memory reduction
- Works with files larger than RAM
- OS-managed memory mapping

**Trade-offs:**

- Requires file-based sources
- Slower for small files (overhead)

**Example:**

```python
engine = Engine()

def jsonl_source():
    with open("products.jsonl", "r") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

engine.register("products", jsonl_source, filename="products.jsonl")
```

---

### Option 4: Enable Merge Join (For Sorted Data)

**When to use**: Pre-sorted data, memory-constrained environments

```python
engine = Engine()
engine.register("products", source, ordered_by="id")  # Merge join enabled
```

**Benefits:**

- Lowest memory usage (no index needed)
- Fast for sorted data
- Streaming algorithm

**Trade-offs:**

- Requires pre-sorted data
- Both tables must be sorted

**Example:**

```python
engine = Engine()

# Data must be sorted by join key
def sorted_users():
    # Users sorted by id
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ])

def sorted_orders():
    # Orders sorted by user_id
    return iter([
        {"id": 1, "user_id": 1, "total": 100},
        {"id": 2, "user_id": 2, "total": 200},
    ])

engine.register("users", sorted_users, ordered_by="id")
engine.register("orders", sorted_orders, ordered_by="user_id")
```

---

## Advanced: Mixing Options

### Mix 1: MMAP with Polars Index Building (Best for Large Files)

**Important Note:** When `use_polars=False` (default), the engine uses **MMAP Join** or **Merge Join** when available. When `use_polars=True` is explicitly set, the engine uses **Polars Join** (not MMAP Join).

However, **MMAP can use Polars internally** for faster index building even when `use_polars=False`:

```python
engine = Engine(use_polars=False)  # MMAP Join will be used
engine.register("products", source, filename="products.jsonl")  # MMAP for memory
# MMAP will use Polars internally for index building if available
```

**What You Get:**

- Low memory (MMAP 90-99% reduction)
- Fast index building (if Polars is installed, used internally)
- Best balance for large files with memory constraints

**Performance:**

- Time: 8-15s for 500MB files (with Polars for index building)
- Memory: 0.01 MB (vs 500MB+ without MMAP)

**When to Use:**

- Large files (> 100MB)
- Memory-constrained systems
- When you want MMAP Join (not Polars Join)

**Note:** If you set `use_polars=True`, the engine will use **Polars Join** instead of MMAP Join, prioritizing speed over memory efficiency.

---

### Mix 2: Polars + Column Pruning (For Wide Tables)

**Optimize for tables with many columns:**

```python
engine = Engine(use_polars=True)

def optimized_source(dynamic_columns=None):
    # Only read requested columns
    if dynamic_columns:
        columns = dynamic_columns
    else:
        columns = ["id", "name", "price", "description", "category", ...]  # All columns

    for row in read_data(columns):
        yield row

engine.register("products", optimized_source)
```

**What You Get:**

- Reduced I/O (only reads needed columns)
- Faster queries (less data to process)
- Lower memory usage

---

### Mix 3: Polars + Filter Pushdown (For Selective Queries)

**Optimize when queries filter most rows:**

```python
engine = Engine(use_polars=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Apply WHERE clause at source level
    query = "SELECT * FROM products"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"

    for row in execute_query(query):
        yield row

engine.register("products", optimized_source)
```

**What You Get:**

- Early filtering (reduces data volume)
- Faster execution (less data to process)
- Lower memory usage

---

### Mix 4: All Optimizations Combined

**The Ultimate Configuration** for maximum performance:

```python
engine = Engine(use_polars=True)

def ultimate_source(dynamic_where=None, dynamic_columns=None):
    """
    Source with all optimizations:
    - Filter pushdown (dynamic_where)
    - Column pruning (dynamic_columns)
    - Data normalization (for Polars)
    """
    # Build optimized query
    query = build_query(dynamic_where, dynamic_columns)

    for row in execute_query(query):
        # Normalize types for Polars stability
        yield normalize_types(row)

engine.register("products", ultimate_source, filename="products.jsonl")
```

**What You Get:**

- Polars Join (speed) - when `use_polars=True`
- Column Pruning (I/O)
- Filter Pushdown (early filtering)

**Best for:** Very large datasets (> 1M rows) when speed is priority

**Note:** This uses Polars Join, not MMAP Join. For memory-constrained scenarios, use `use_polars=False` with `filename` parameter instead.

---

## Performance Guide

### By Dataset Size

| Size              | Configuration                   | Why                                       |
| ----------------- | ------------------------------- | ----------------------------------------- |
| **< 10K rows**    | `use_polars=False` (default)    | Fastest, most stable                      |
| **10K-100K rows** | `use_polars=False` (default)    | Still fastest, handles mixed types        |
| **100K-1M rows**  | `use_polars=True` OR `filename` | Polars Join (speed) OR MMAP Join (memory) |
| **> 1M rows**     | All optimizations               | Maximum performance                       |

### By Priority

**Priority: Stability** - Use default (`use_polars=False`)

```python
engine = Engine()  # Most stable
```

**Priority: Speed** - Use Polars

```python
engine = Engine(use_polars=True)  # Fastest for large datasets
```

**Priority: Memory** - Use MMAP

```python
engine = Engine()
engine.register("table", source, filename="data.jsonl")  # Lowest memory
```

**Priority: Both** - Choose based on priority:

**If speed is more important:**

```python
engine = Engine(use_polars=True)  # Uses Polars Join (fastest)
engine.register("table", source)  # No filename - Polars Join
```

**If memory is more important:**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join (lowest memory)
engine.register("table", source, filename="data.jsonl")  # MMAP Join
```

**Note:** Polars Join and MMAP Join are mutually exclusive - the engine chooses one based on `use_polars` flag. MMAP Join can use Polars internally for index building, but the join algorithm itself is MMAP.

---

## Learning Path

### Level 1: Beginner (Start Here)

```python
# Most stable configuration
engine = Engine()  # Default: use_polars=False
engine.register("table1", source1)
engine.register("table2", source2)
```

**Learn:**

- Basic source registration
- Simple SQL queries
- How joins work

---

### Level 2: Intermediate

```python
# Add debug mode to see what's happening
engine = Engine(debug=True)

# Experiment with Polars for large datasets
engine = Engine(use_polars=True)
```

**Learn:**

- Debug output
- When to use Polars
- Data normalization

---

### Level 3: Advanced

```python
# Use MMAP for large files (requires use_polars=False)
engine = Engine(use_polars=False)  # MMAP Join requires use_polars=False
engine.register("table", source, filename="data.jsonl")

# Use Merge Join for sorted data
engine.register("table", source, ordered_by="key")
```

**Learn:**

- MMAP for memory efficiency
- Merge Join for sorted data
- Protocol optimizations

---

### Level 4: Expert

```python
# All optimizations combined
engine = Engine(use_polars=True)

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Filter pushdown + Column pruning
    pass

engine.register("table", optimized_source, filename="data.jsonl")
```

**Learn:**

- Protocol-based optimizations
- Combining all options
- Maximum performance tuning

---

## Common Pitfalls

### Pitfall 1: Using Polars Without Normalization

**Problem:**

```python
engine = Engine(use_polars=True)
# Mixed types cause schema inference errors
```

**Solution:**

```python
def normalized_source():
    for row in raw_source():
        yield {
            "id": int(row.get("id", 0)),
            "price": float(row.get("price", 0.0)),
        }
```

---

### Pitfall 2: Using MMAP Without Polars (Very Slow)

**Problem:**

```python
engine = Engine(use_polars=False)
engine.register("table", source, filename="data.jsonl")  # Very slow!
```

**Solution:**

```python
engine = Engine(use_polars=True)  # Polars speeds up MMAP index building
engine.register("table", source, filename="data.jsonl")
```

---

### Pitfall 3: Using MMAP for Small Files

**Problem:**

```python
# MMAP overhead > benefit for small files
engine.register("table", source, filename="small.jsonl")  # Slower!
```

**Solution:**

```python
# No filename for small files
engine.register("table", source)  # Faster for < 100MB
```

---

## Quick Decision Guide

- **Just starting?** Use default (`Engine()`)
- **Have large datasets?** Use `use_polars=True`
- **Memory constrained?** Use `filename` parameter (MMAP)
- **Data is sorted?** Use `ordered_by` parameter (Merge Join)
- **Want maximum performance?** Use `use_polars=True` + protocols (Polars Join) OR `use_polars=False` + `filename` (MMAP Join) + protocols

---

## Real-World Example: Complete Workflow

### Step 1: Start Simple (Most Secure)

```python
from streaming_sql_engine import Engine

# Start with default (most stable)
engine = Engine()

def postgres_users():
    # Your PostgreSQL code
    pass

def mysql_orders():
    # Your MySQL code
    pass

engine.register("users", postgres_users)
engine.register("orders", mysql_orders)

results = engine.query("SELECT * FROM users JOIN orders ON users.id = orders.user_id")
```

### Step 2: Add Debug Mode (Understand What's Happening)

```python
engine = Engine(debug=True)  # See execution details
```

### Step 3: Optimize for Your Use Case

**If you have large datasets:**

```python
engine = Engine(use_polars=True)  # Enable Polars
```

**If you have large files:**

```python
engine = Engine(use_polars=False)  # MMAP Join requires use_polars=False
engine.register("table", source, filename="data.jsonl")  # Enable MMAP
```

**If you have sorted data:**

```python
engine.register("table", source, ordered_by="key")  # Enable Merge Join
```

### Step 4: Combine Optimizations

**For Speed Priority (Polars Join):**

```python
engine = Engine(use_polars=True)  # Uses Polars Join

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Supports all optimizations
    pass

engine.register("table", optimized_source)  # No filename - Polars Join
```

**For Memory Priority (MMAP Join):**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join

def optimized_source(dynamic_where=None, dynamic_columns=None):
    # Supports all optimizations
    pass

engine.register("table", optimized_source, filename="data.jsonl")  # MMAP Join
```

---

## Summary

### Start Here (Most Secure)

```python
engine = Engine()  # Default: use_polars=False
engine.register("table1", source1)
engine.register("table2", source2)
```

**Why:** Most stable, handles all edge cases, works with any data types

---

### Then Experiment

1. **Add debug mode**: `Engine(debug=True)` - See what's happening
2. **Try Polars**: `Engine(use_polars=True)` - For large datasets
3. **Try MMAP**: `filename="data.jsonl"` - For large files
4. **Try Merge Join**: `ordered_by="key"` - For sorted data

---

### Advanced: Mix Options

**Best Mix for Large Files:**

**Option 1: Speed Priority (Polars Join)**

```python
engine = Engine(use_polars=True)  # Uses Polars Join (fastest)
engine.register("table", source)  # No filename needed
```

**Option 2: Memory Priority (MMAP Join)**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join (lowest memory)
engine.register("table", source, filename="data.jsonl")  # MMAP enabled
```

**Best Mix for Maximum Performance:**

**Option 1: Speed Priority (Polars Join + Protocols)**

```python
engine = Engine(use_polars=True)  # Uses Polars Join

def source(dynamic_where=None, dynamic_columns=None):
    # All optimizations (filter pushdown + column pruning)
    pass

engine.register("table", source)  # No filename - Polars Join
```

**Option 2: Memory Priority (MMAP Join + Protocols)**

```python
engine = Engine(use_polars=False)  # Uses MMAP Join

def source(dynamic_where=None, dynamic_columns=None):
    # All optimizations (filter pushdown + column pruning)
    pass

engine.register("table", source, filename="data.jsonl")  # MMAP Join
```

---

## Key Takeaways

1. **Start Simple**: Use default configuration (`Engine()`) - it's the most stable
2. **Experiment Gradually**: Add options one at a time to understand their impact
3. **Mix Wisely**: Choose Polars Join (speed) OR MMAP Join (memory) based on priority
4. **Know When to Use Each**: Small files: default, Large files: Polars Join (speed) OR MMAP Join (memory)

---

**Remember**: Start with the default configuration, then experiment with options as you understand your data and performance needs better.

## Getting Started

Installation:

```bash
pip install streaming-sql-engine
```

Quick start:

```python
from streaming_sql_engine import Engine

engine = Engine()

# Register data sources (any Python function that returns an iterator)
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

**For database connections**, create iterator functions:

```python
from streaming_sql_engine import Engine
import psycopg2

engine = Engine()

# Register database table (iterator function)
def users_source():
    conn = psycopg2.connect(host="localhost", database="mydb", user="user", password="pass")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE active = true")
    for row in cursor:
        yield {"id": row[0], "name": row[1], "email": row[2]}
    conn.close()

engine.register("users", users_source)

# Query
for row in engine.query("SELECT * FROM users WHERE users.active = true"):
    print(row)
```

---

## Conclusion

The Streaming SQL Engine fills a unique niche: **cross-system data integration**. While it may not match the raw performance of specialized tools for their specific use cases, it excels at joining data from different systems — a problem that traditional databases cannot solve.

**Key strengths:**

- Cross-system joins (databases, APIs, files)
- Zero infrastructure requirements
- Memory-efficient streaming architecture
- Python-native integration
- Automatic optimizations
- Simple deployment

**Best suited for:**

- Microservices data aggregation
- Cross-system ETL pipelines
- Real-time data integration
- Memory-constrained environments
- Python-native workflows

For cross-system data integration, the Streaming SQL Engine provides a unique solution that balances performance, simplicity, and flexibility.

---

## Resources

- **PyPI:** `pip install streaming-sql-engine`

---
