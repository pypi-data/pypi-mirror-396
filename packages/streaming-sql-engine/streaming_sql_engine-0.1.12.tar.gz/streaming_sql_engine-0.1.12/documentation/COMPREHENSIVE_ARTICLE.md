# Streaming SQL Engine: A Comprehensive Guide

## Introduction

The Streaming SQL Engine is a lightweight Python library that enables SQL-style joins across heterogeneous data sources. Unlike traditional databases that require all data to be in one place, this engine allows you to join data from databases, APIs, files, and custom Python functions using standard SQL syntax, all while processing data row-by-row without loading entire tables into memory.

This article explores the best use cases, performance characteristics, features, and advantages of the Streaming SQL Engine compared to alternatives like Apache Spark, DuckDB, and Apache Flink.

---

## Part 1: Best Use Cases

### 1. Cross-System Data Integration

The primary strength of the Streaming SQL Engine is joining data from completely different systems that cannot be connected directly through traditional database queries.

**Example: Joining MySQL + PostgreSQL + MongoDB + REST API**

```python
from streaming_sql_engine import Engine
from examples.database_helpers import create_table_source

engine = Engine()

# Register MySQL source
mysql_pool = create_mysql_pool_from_env()
engine.register("mysql_products", create_table_source(mysql_pool, "products"))

# Register PostgreSQL source
pg_pool = create_postgresql_pool_from_env()
engine.register("postgres_users", create_table_source(pg_pool, "users"))

# Register MongoDB source
def mongo_source():
    # MongoDB connection logic
    pass
engine.register("mongo_inventory", mongo_source)

# Register REST API source
def api_prices():
    import requests
    response = requests.get("https://api.example.com/prices")
    for item in response.json():
        yield item
engine.register("api_prices", api_prices)

# Join across all sources in a single SQL query
query = """
    SELECT
        p.name,
        u.email,
        i.quantity,
        a.price
    FROM mysql_products p
    JOIN postgres_users u ON p.user_id = u.id
    JOIN mongo_inventory i ON p.sku = i.sku
    JOIN api_prices a ON p.sku = a.sku
    WHERE p.price > 100
"""

for row in engine.query(query):
    process(row)
```

**Why this is ideal:** Traditional databases cannot execute this query because the data resides in different systems. The Streaming SQL Engine bridges this gap by providing a unified SQL interface.

### 2. Database + File System Integration

Joining database records with files (CSV, JSONL, JSON, XML) is a common requirement in data pipelines.

**Example: Database + XML Files**

```python
# Real-world example: Comparing prices between XML files and matching with MongoDB
def parse_xml_file(filepath):
    # Parse XML and yield product dictionaries
    pass

engine.register("xml1", lambda: parse_xml_file("prices1.xml"))
engine.register("xml2", lambda: parse_xml_file("prices2.xml"))
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

**Performance:** In production, this handles 17 million XML records joined with 5 million MongoDB records in approximately 7 minutes using 400 MB RAM, demonstrating efficient memory usage for cross-system joins.

### 3. Real-Time Data Processing

The engine excels at joining streaming or real-time data sources with static reference data.

**Example: Live API + Database Reference**

```python
def live_api_source():
    """Source that fetches live data"""
    while True:
        yield fetch_latest_from_api()
        time.sleep(1)

engine.register("live_data", live_api_source)
engine.register("static_reference", create_table_source(pool, "reference"))

# Join live data with static reference
for row in engine.query("""
    SELECT live_data.*, static_reference.category
    FROM live_data
    JOIN static_reference ON live_data.id = static_reference.id
"""):
    process_live(row)
```

### 4. Memory-Constrained Environments

When processing large datasets that exceed available memory, the streaming architecture processes data row-by-row without materializing full tables.

**Example: Large File Processing**

```python
# Process millions of records without loading into memory
engine.register("huge_file", lambda: read_jsonl("large_file.jsonl"),
                filename="large_file.jsonl")  # Enables memory-mapped joins

for row in engine.query("SELECT * FROM huge_file WHERE condition = 'value'"):
    process_and_discard(row)  # Process immediately, don't store
```

### 5. Microservices Data Aggregation

In microservices architectures, data is distributed across multiple services. The engine enables joining this data without requiring a shared database.

**Example: Multiple Service Integration**

```python
# Service 1: User service (PostgreSQL)
engine.register("users", create_table_source(user_pool, "users"))

# Service 2: Order service (MySQL)
engine.register("orders", create_table_source(order_pool, "orders"))

# Service 3: Payment service (REST API)
def payment_source():
    # Fetch from payment service API
    pass
engine.register("payments", payment_source)

# Join across services
query = """
    SELECT users.name, orders.total, payments.status
    FROM users
    JOIN orders ON users.id = orders.user_id
    JOIN payments ON orders.id = payments.order_id
"""
```

### 6. Python Processing Between Joins

When you need to apply Python logic or transformations between join operations, the engine provides flexibility.

**Example: Enriched Data Processing**

```python
def enriched_source():
    """Source that processes data with Python before joining"""
    for row in stream_query(pool, "SELECT * FROM products"):
        # Apply Python logic
        row['enriched_score'] = calculate_score(row)
        row['processed_data'] = process_with_python(row)
        yield row

engine.register("enriched_products", enriched_source)
engine.register("categories", create_table_source(pool, "categories"))

query = """
    SELECT p.name, p.enriched_score, c.category_name
    FROM enriched_products p
    JOIN categories c ON p.category_id = c.id
"""
```

---

## Part 2: Performance and Metrics

### Real-World Performance Example

**Scenario:** Comparing prices between two XML files (17 million records each) and matching with MongoDB collection (5 million records).

**Results:**

- **Execution Time:** 7 minutes (420 seconds)
- **Memory Usage:** 400 MB
- **CPU Usage:** 79%
- **Throughput:** ~92,857 records/second (~5.57 million records/minute)

**Analysis:**

**Memory Efficiency:** Processing 39 million total records with only 400 MB RAM demonstrates exceptional memory efficiency. This equates to approximately 10 bytes per record on average, indicating:

- Effective streaming architecture (no full table materialization)
- Successful column pruning (only extracting needed columns)
- Efficient index building for joins
- Proper memory management throughout the pipeline

**CPU Utilization:** 79% CPU usage indicates the engine is CPU-bound rather than I/O-bound, meaning:

- The engine is actively processing data
- Network/file I/O is not the bottleneck
- Python processing overhead is acceptable for the use case

**Performance Comparison:**

| Metric                     | Streaming SQL Engine | Direct Database Query   |
| -------------------------- | -------------------- | ----------------------- |
| Cross-system joins         | Possible             | Not possible            |
| Same-database joins        | 7 minutes            | 30-60 seconds           |
| Memory usage (39M records) | 400 MB               | Database manages        |
| Setup complexity           | Zero infrastructure  | Requires database setup |

### Performance Optimizations

The engine includes several automatic optimizations:

**1. Column Pruning**

- Only extracts columns needed for the query
- Reduces I/O and memory for wide tables
- Automatic based on SELECT and WHERE clauses

**2. Filter Pushdown**

- Pushes WHERE conditions to data sources when possible
- Reduces data transfer from databases
- Applies to root table conditions

**3. Polars Vectorization**

- 10-200x faster for large datasets
- SIMD-accelerated filtering and projections
- Batch processing for better cache locality
- Enabled by default

**4. Memory-Mapped Joins**

- 90-99% memory reduction for large JSONL files
- Uses operating system virtual memory
- Enables processing files larger than RAM

**5. Merge Joins**

- Efficient joins when both sides are sorted
- O(n+m) time complexity
- Better cache locality than hash joins

**6. Lookup Joins**

- Default join strategy for unsorted data
- Builds hash index on right side
- O(1) lookup time per left row

### Performance Benchmarks

| Operation           | Records | Time      | Memory | Notes                  |
| ------------------- | ------- | --------- | ------ | ---------------------- |
| XML + XML + MongoDB | 39M     | 7 min     | 400 MB | Cross-system joins     |
| Database + Database | 1M      | 5-10 sec  | Varies | Different databases    |
| File + File         | 10M     | 2-5 min   | 200 MB | Memory-mapped joins    |
| API + Database      | 100K    | 10-30 sec | 50 MB  | Network latency factor |

---

## Part 3: Features

### SQL Support

**Supported SQL Features:**

- **SELECT:** Column selection, aliasing, table-qualified columns (`table.column`)
- **FROM:** Single table with optional alias
- **JOIN:** INNER JOIN, LEFT JOIN with equality conditions
- **WHERE:** Comparisons (`=`, `!=`, `<`, `>`, `<=`, `>=`), boolean logic (`AND`, `OR`, `NOT`), NULL checks (`IS NULL`, `IS NOT NULL`), IN clauses
- **Multiple Joins:** Sequential joins of any number of tables
- **Arithmetic Operations:** Addition, subtraction, multiplication, division, modulo

**Not Supported:**

- GROUP BY, aggregations (COUNT, SUM, AVG, etc.)
- ORDER BY
- HAVING
- UNION
- Subqueries
- Non-equality joins (range joins, etc.)

### Data Source Support

**Databases:**

- PostgreSQL (via connection pools)
- MySQL (via connection pools)
- MongoDB (via pymongo)

**Files:**

- JSONL (JSON Lines)
- CSV
- JSON
- XML (via custom parsers)

**APIs:**

- REST APIs (any HTTP endpoint)
- GraphQL (via custom functions)
- Any Python function returning an iterator

**Custom Sources:**

- Any Python generator function
- Any iterable data structure

### Protocol-Based Optimization

The engine automatically detects and applies optimizations through a protocol-based system:

**Filter Pushdown Protocol:**

```python
def source(dynamic_where=None, dynamic_columns=None):
    # Engine automatically passes WHERE clause
    if dynamic_where:
        query = f"SELECT * FROM table WHERE {dynamic_where}"
    # Source filters before returning data
```

**Column Pruning Protocol:**

```python
def source(dynamic_where=None, dynamic_columns=None):
    # Engine automatically requests only needed columns
    if dynamic_columns:
        columns = ", ".join(dynamic_columns)
        query = f"SELECT {columns} FROM table"
```

**Automatic Detection:** The engine automatically detects if a source function accepts `dynamic_where` and `dynamic_columns` parameters and applies optimizations accordingly. No flags or configuration needed.

### Join Algorithms

**1. Lookup Join (Default)**

- Builds hash index on right side
- O(1) lookup per left row
- Best for: Unsorted data, right side fits in memory

**2. Merge Join**

- Requires both sides sorted by join key
- O(n+m) time complexity
- Best for: Pre-sorted data, memory-efficient

**3. Memory-Mapped Join**

- Uses OS virtual memory for large files
- 90-99% memory reduction
- Best for: Very large JSONL files

**4. Polars Join**

- Vectorized batch processing
- SIMD-accelerated
- Best for: Large datasets, multiple joins

### Execution Model

**Streaming Architecture:**

- Processes data row-by-row
- Never materializes full tables
- Results yielded immediately as generators
- Low memory footprint

**Iterator Pipeline:**

```
ScanIterator → FilterIterator → JoinIterators → ProjectIterator → Results
```

Each iterator processes rows incrementally, enabling true streaming execution.

### Debug Mode

Enable detailed execution information:

```python
engine = Engine(debug=True)
```

Shows:

- SQL parsing steps
- Logical plan construction
- Optimization applications
- Join algorithm selection
- Row processing progress

---

## Part 4: Advantages Over Alternatives

### vs Apache Spark / PySpark

**Streaming SQL Engine Advantages:**

1. **Zero Infrastructure**

   - No cluster setup required
   - No distributed system configuration
   - Works on a single machine
   - No JVM overhead

2. **Simpler Deployment**

   - Pure Python library
   - Install via pip
   - No Hadoop/Spark cluster needed
   - Lower operational complexity

3. **Lower Latency**

   - No cluster startup time
   - Immediate execution
   - Better for real-time processing
   - No network overhead for single-machine use

4. **Cross-System Joins**

   - Native support for APIs, files, databases
   - No need to import data into Spark
   - Direct connection to any Python data source

5. **Memory Efficiency**
   - Streaming row-by-row processing
   - Lower memory footprint for single queries
   - No Spark executor overhead

**Specific Cases Where Streaming SQL Engine is Better:**

**Case 1: Joining Live APIs with Databases**

**Problem:** You need to join real-time API data with database records. Spark requires importing API data first.

**With Spark:**

```python
# Step 1: Fetch API data and save to file/DataFrame
api_data = fetch_from_api()
spark_df = spark.createDataFrame(api_data)

# Step 2: Read database data
db_df = spark.read.jdbc(url, table)

# Step 3: Join
result = db_df.join(api_df, "id")
```

**Issues:** Requires Spark cluster, data import step, higher latency

**With Streaming SQL Engine:**

```python
# Direct join - no import needed
def api_source():
    for item in fetch_from_api():
        yield item

engine.register("api_data", api_source)
engine.register("db_data", create_table_source(pool, "table"))

# Immediate join, no cluster needed
for row in engine.query("SELECT * FROM api_data JOIN db_data ON ..."):
    process(row)
```

**Advantages:** No cluster, immediate execution, lower latency, simpler code

**Case 2: Microservices Data Integration**

**Problem:** Data is distributed across multiple microservices (different databases, APIs). Spark requires exporting all data first.

**With Spark:**

```python
# Must export from each service first
service1_df = spark.read.jdbc(service1_db, "table1")
service2_df = spark.read.jdbc(service2_db, "table2")
service3_df = spark.read.json("api_export.json")  # Must export API first

# Then join
result = service1_df.join(service2_df, "id").join(service3_df, "id")
```

**Issues:** Requires data export/import, Spark cluster, ETL pipeline complexity

**With Streaming SQL Engine:**

```python
# Direct joins across services - no export needed
engine.register("service1", create_table_source(service1_pool, "table1"))
engine.register("service2", create_table_source(service2_pool, "table2"))
engine.register("service3", lambda: fetch_from_service3_api())

# Direct join across services
query = """
    SELECT s1.*, s2.*, s3.*
    FROM service1 s1
    JOIN service2 s2 ON s1.id = s2.id
    JOIN service3 s3 ON s1.id = s3.id
"""
```

**Advantages:** No data export, direct connections, real-time joins, simpler architecture

**Case 3: Ad-Hoc Cross-System Queries**

**Problem:** You need to quickly join data from different systems for analysis. Spark requires cluster setup and data import.

**With Spark:**

- Setup: Configure Spark cluster (minutes to hours)
- Import: Export data from each system, import into Spark
- Query: Execute join
- **Total time:** Hours to days for first query

**With Streaming SQL Engine:**

- Setup: `pip install streaming-sql-engine` (seconds)
- Import: None needed - direct connections
- Query: Execute join immediately
- **Total time:** Minutes for first query

**Case 4: Memory-Constrained Environments**

**Problem:** Limited memory available, cannot run Spark cluster.

**With Spark:**

- Requires: Multiple JVM processes, executor memory, driver memory
- Minimum: 4-8 GB RAM for small cluster
- Overhead: High memory footprint even for small queries

**With Streaming SQL Engine:**

- Requires: Single Python process
- Minimum: 100-500 MB RAM for queries
- Overhead: Minimal - only processes active rows
- **Real example:** 39M records processed with 400 MB RAM

**Case 5: Python-Native Workflows**

**Problem:** You're working in Python and need to join data. Spark requires PySpark API learning curve.

**With Spark:**

```python
# PySpark API - different from standard Python
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("app").getOrCreate()
df1 = spark.read.jdbc(...)
df2 = spark.read.json(...)
result = df1.join(df2, "id").collect()  # Returns list, not iterator
```

**Issues:** Different API, learning curve, returns all results at once

**With Streaming SQL Engine:**

```python
# Standard Python - familiar syntax
from streaming_sql_engine import Engine
engine = Engine()
engine.register("table1", source1)
engine.register("table2", source2)

# Standard SQL, Python iterators
for row in engine.query("SELECT * FROM table1 JOIN table2 ON ..."):
    process(row)  # Standard Python processing
```

**Advantages:** Familiar Python syntax, standard SQL, iterator-based (memory efficient)

**When to Use Spark Instead:**

- Need distributed processing across multiple machines
- Require complex aggregations and GROUP BY
- Processing petabytes of data
- Need fault tolerance and recovery
- Batch processing large datasets
- Complex ETL pipelines with transformations

**When to Use Streaming SQL Engine:**

- Cross-system joins (databases, APIs, files)
- Single-machine processing
- Real-time or low-latency requirements
- Simple deployment requirements
- Python-native workflows
- Ad-hoc queries across systems
- Memory-constrained environments
- Microservices data integration

### vs DuckDB

**Streaming SQL Engine Advantages:**

1. **Cross-System Integration**

   - Native support for APIs and custom Python functions
   - No need to import data into DuckDB
   - Direct connection to any Python data source
   - Real-time data joining

2. **Streaming Architecture**

   - True row-by-row processing
   - Lower memory footprint
   - Better for real-time data
   - No materialization required

3. **Python Ecosystem Integration**

   - Pure Python implementation
   - Easy integration with Python libraries
   - Custom Python processing between joins
   - Native Python data types

4. **Flexible Data Sources**

   - Any Python iterator works
   - No format conversion needed
   - Dynamic data sources (APIs, generators)
   - Custom transformation functions

5. **Simpler for Cross-System Use Cases**
   - No need to export/import data
   - Direct joins across systems
   - Unified SQL interface for heterogeneous sources

**Specific Cases Where Streaming SQL Engine is Better:**

**Case 1: Joining REST APIs with Databases**

**Problem:** You need to join live API data with database records. DuckDB requires importing API data first.

**With DuckDB:**

```python
import duckdb
import requests

# Step 1: Fetch API data
api_response = requests.get("https://api.example.com/products")
api_data = api_response.json()

# Step 2: Import into DuckDB
conn = duckdb.connect()
conn.execute("CREATE TABLE api_data AS SELECT * FROM api_data")  # Must import first

# Step 3: Read database
db_data = conn.execute("SELECT * FROM postgres_scan('db', 'products')").fetchdf()

# Step 4: Join
result = conn.execute("""
    SELECT * FROM api_data a
    JOIN db_data d ON a.id = d.id
""").fetchdf()
```

**Issues:** Requires data import, not real-time, must materialize API data

**With Streaming SQL Engine:**

```python
# Direct join - no import needed
def api_source():
    response = requests.get("https://api.example.com/products")
    for item in response.json():
        yield item

engine.register("api_data", api_source)
engine.register("db_data", create_table_source(pool, "products"))

# Immediate join, always fresh data
for row in engine.query("SELECT * FROM api_data JOIN db_data ON api_data.id = db_data.id"):
    process(row)
```

**Advantages:** No import step, real-time data, simpler code, lower memory

**Case 2: Joining Multiple Different Databases**

**Problem:** You need to join MySQL + PostgreSQL + MongoDB. DuckDB requires exporting/importing from each.

**With DuckDB:**

```python
# Must use separate connectors and import
mysql_data = duckdb.execute("SELECT * FROM mysql_scan('mysql://...', 'table1')").fetchdf()
pg_data = duckdb.execute("SELECT * FROM postgres_scan('pg://...', 'table2')").fetchdf()

# MongoDB requires export to file first
# mongoexport --collection=table3 --out=table3.json
mongo_data = duckdb.execute("SELECT * FROM read_json('table3.json')").fetchdf()

# Then join
result = duckdb.execute("""
    SELECT * FROM mysql_data m
    JOIN pg_data p ON m.id = p.id
    JOIN mongo_data mg ON m.id = mg.id
""").fetchdf()
```

**Issues:** Complex setup, data export required for MongoDB, not real-time

**With Streaming SQL Engine:**

```python
# Direct connections - no export needed
engine.register("mysql_data", create_table_source(mysql_pool, "table1"))
engine.register("pg_data", create_table_source(pg_pool, "table2"))
engine.register("mongo_data", mongo_source)  # Direct MongoDB connection

# Direct join across all databases
query = """
    SELECT * FROM mysql_data m
    JOIN pg_data p ON m.id = p.id
    JOIN mongo_data mg ON m.id = mg.id
"""
for row in engine.query(query):
    process(row)
```

**Advantages:** No export needed, direct connections, real-time joins, unified interface

**Case 3: Real-Time Streaming Data**

**Problem:** You need to join live streaming data (e.g., Kafka, WebSockets) with reference data.

**With DuckDB:**

```python
# Must buffer streaming data first
stream_buffer = []
for message in kafka_consumer:
    stream_buffer.append(message)
    if len(stream_buffer) > 10000:
        # Import batch into DuckDB
        conn.execute("INSERT INTO stream_data SELECT * FROM stream_buffer")
        # Then join
        result = conn.execute("SELECT * FROM stream_data JOIN ref_data ...")
```

**Issues:** Requires buffering, not true streaming, higher latency

**With Streaming SQL Engine:**

```python
# True streaming - no buffering needed
def stream_source():
    for message in kafka_consumer:
        yield message  # Yield immediately

engine.register("stream_data", stream_source)
engine.register("ref_data", create_table_source(pool, "reference"))

# Real-time join - processes as data arrives
for row in engine.query("SELECT * FROM stream_data JOIN ref_data ON ..."):
    process_immediately(row)  # No buffering
```

**Advantages:** True streaming, lower latency, no buffering required

**Case 4: Custom Python Processing Between Joins**

**Problem:** You need to apply Python logic (ML models, custom functions) between join operations.

**With DuckDB:**

```python
# Limited Python integration - must use UDFs or export
def custom_process(row):
    # Python processing
    return processed_row

# Must export to Python, process, re-import
data = conn.execute("SELECT * FROM table1").fetchdf()
processed = data.apply(custom_process, axis=1)  # Process in Python
conn.execute("CREATE TABLE processed AS SELECT * FROM processed")  # Re-import
result = conn.execute("SELECT * FROM processed JOIN table2 ...")
```

**Issues:** Export/import overhead, not seamless Python integration

**With Streaming SQL Engine:**

```python
# Seamless Python processing
def enriched_source():
    for row in db_source():
        row['ml_score'] = ml_model.predict(row)  # Python ML model
        row['custom_field'] = custom_function(row)  # Custom Python logic
        yield row

engine.register("enriched_data", enriched_source)
engine.register("table2", create_table_source(pool, "table2"))

# Python processing happens naturally in the pipeline
for row in engine.query("SELECT * FROM enriched_data JOIN table2 ON ..."):
    process(row)
```

**Advantages:** Native Python integration, no export/import, seamless processing

**Case 5: Dynamic Data Sources**

**Problem:** Data sources change dynamically (different APIs, conditional sources, generators).

**With DuckDB:**

```python
# Must know all sources upfront and import
if condition:
    source1 = duckdb.execute("SELECT * FROM read_csv('file1.csv')").fetchdf()
else:
    source1 = duckdb.execute("SELECT * FROM read_json('file2.json')").fetchdf()

# Static import - not dynamic
```

**Issues:** Static data sources, must import all upfront

**With Streaming SQL Engine:**

```python
# Dynamic sources - can change at runtime
def dynamic_source():
    if condition:
        for row in api_source():
            yield row
    else:
        for row in file_source():
            yield row

engine.register("dynamic_data", dynamic_source)

# Works with any Python generator
for row in engine.query("SELECT * FROM dynamic_data JOIN ..."):
    process(row)
```

**Advantages:** Dynamic sources, runtime flexibility, any Python generator works

**Case 6: Memory-Constrained Environments**

**Problem:** Limited memory available. DuckDB materializes dataframes in memory.

**With DuckDB:**

- Materializes entire dataframes
- For 10M rows: ~500 MB - 2 GB depending on columns
- Must fit all data in memory

**With Streaming SQL Engine:**

- Processes row-by-row
- For 10M rows: ~50-200 MB (only active rows)
- Can process data larger than RAM
- **Real example:** 39M records with 400 MB RAM

**Performance Comparison:**

| Scenario                | DuckDB             | Streaming SQL Engine | Winner                  |
| ----------------------- | ------------------ | -------------------- | ----------------------- |
| Same-database joins     | 0.1-1s             | 5-10s                | DuckDB (10-100x faster) |
| Cross-system joins      | Requires import    | Direct join          | Streaming Engine        |
| API + Database join     | Must export API    | Direct join          | Streaming Engine        |
| Real-time data          | Buffering required | True streaming       | Streaming Engine        |
| Python processing       | Export/import      | Native               | Streaming Engine        |
| Memory usage (10M rows) | 500 MB - 2 GB      | 50-200 MB            | Streaming Engine        |
| Setup complexity        | Medium             | Low                  | Streaming Engine        |

**When to Use DuckDB Instead:**

- All data can be imported into DuckDB
- Need GROUP BY and aggregations
- Require maximum query performance
- Complex analytical queries
- OLAP workloads
- Data science / analytics workflows
- Single data source queries

**When to Use Streaming SQL Engine:**

- Data in different systems (can't import)
- Need to join APIs with databases
- Real-time or streaming data
- Python-native processing required
- Cross-system integration
- Dynamic data sources
- Memory-constrained environments
- Custom Python processing needed

### vs Apache Flink

**Streaming SQL Engine Advantages:**

1. **Simpler Architecture**

   - No cluster setup
   - No distributed system complexity
   - Single-machine execution
   - Lower operational overhead

2. **Python-Native**

   - Pure Python implementation
   - Easy integration with Python ecosystem
   - No JVM required
   - Familiar Python APIs

3. **Cross-System Joins**

   - Native support for databases, APIs, files
   - No need for connectors
   - Direct Python function integration
   - Flexible data source support

4. **Lower Latency**

   - No cluster startup time
   - Immediate execution
   - Better for ad-hoc queries
   - No network overhead

5. **Easier Deployment**
   - Install via pip
   - No infrastructure requirements
   - Works on any Python environment
   - Lower resource requirements

**When to Use Flink Instead:**

- Need distributed stream processing
- Require exactly-once semantics
- Processing high-throughput streams
- Need complex event-time processing
- Require fault tolerance at scale

**When to Use Streaming SQL Engine:**

- Cross-system joins
- Single-machine processing
- Ad-hoc queries
- Python-native workflows
- Simple deployment requirements

### vs Direct Database Queries

**Streaming SQL Engine Advantages:**

1. **Cross-System Capability**

   - Join different databases
   - Join databases with APIs
   - Join databases with files
   - Unified SQL interface

2. **No Data Migration**
   - No need to export/import data
   - Direct joins across systems
   - Real-time integration
   - No ETL pipeline needed

**When to Use Direct Database Queries:**

- All tables in same database
- Need maximum performance
- Require GROUP BY and aggregations
- Complex SQL features needed

**Performance Comparison:**

| Scenario                         | Direct SQL       | Streaming Engine |
| -------------------------------- | ---------------- | ---------------- |
| Same database, 5 joins, 13M rows | 30-60 seconds    | 7 minutes        |
| Different databases, 5 joins     | Not possible     | 7 minutes        |
| Database + API join              | Not possible     | Possible         |
| Memory usage (39M records)       | Database manages | 400 MB           |

### Summary: When to Choose Streaming SQL Engine

**Choose Streaming SQL Engine when:**

- Joining data from different systems (databases, APIs, files)
- Need Python-native processing
- Require simple deployment (no infrastructure)
- Processing real-time or streaming data
- Memory-constrained environments
- Cross-system data integration

**Choose alternatives when:**

- All data in same database → Use direct SQL
- Need distributed processing → Use Spark/Flink
- Need aggregations → Use DuckDB/database
- Maximum performance for same-database → Use database directly
- Petabyte-scale data → Use Spark/Flink

---

## Conclusion

The Streaming SQL Engine fills a unique niche in the data processing ecosystem. While it may not match the raw performance of specialized tools for their specific use cases, it excels at cross-system data integration—a problem that traditional databases cannot solve.

**Key Strengths:**

- Cross-system joins (databases, APIs, files)
- Zero infrastructure requirements
- Memory-efficient streaming architecture
- Python-native integration
- Automatic optimizations
- Simple deployment

**Best Suited For:**

- Microservices data aggregation
- Cross-system ETL pipelines
- Real-time data integration
- Memory-constrained environments
- Python-native workflows

The engine demonstrates that sometimes the best tool is not the fastest tool, but the one that solves a problem others cannot. For cross-system data integration, the Streaming SQL Engine provides a unique solution that balances performance, simplicity, and flexibility.

---

## Quick Decision Guide: When to Choose Streaming SQL Engine

### Choose Streaming SQL Engine When:

**1. Cross-System Joins Required**

- Joining MySQL + PostgreSQL + MongoDB
- Joining databases with REST APIs
- Joining databases with files (CSV, JSONL, XML)
- Joining APIs with files
- **Why:** Only tool that can do this without data export/import

**2. Real-Time or Streaming Data**

- Live API data joins
- Kafka/WebSocket stream joins
- Real-time data integration
- **Why:** True streaming architecture, no buffering required

**3. Python-Native Workflows**

- Need custom Python processing between joins
- ML model integration
- Python library integration required
- **Why:** Pure Python, seamless integration

**4. Simple Deployment**

- No infrastructure available
- Single-machine processing
- Quick setup required
- **Why:** Zero infrastructure, pip install, immediate use

**5. Memory Constraints**

- Limited RAM available
- Processing data larger than RAM
- Low memory footprint required
- **Why:** Streaming row-by-row, 400 MB for 39M records

**6. Microservices Architecture**

- Data distributed across services
- No shared database
- Service-to-service joins
- **Why:** Direct connections, no data export needed

### Choose DuckDB When:

- All data can be imported into DuckDB
- Need GROUP BY and aggregations
- Maximum query performance required
- Complex analytical queries
- Single data source queries
- Data science / analytics workflows

### Choose PySpark/Spark When:

- Need distributed processing across machines
- Processing petabytes of data
- Complex ETL pipelines
- Need fault tolerance and recovery
- Batch processing large datasets
- Complex aggregations at scale

### Summary Comparison Table

| Requirement             | Streaming SQL Engine     | DuckDB              | PySpark                    |
| ----------------------- | ------------------------ | ------------------- | -------------------------- |
| Cross-system joins      | ✅ Best                  | ⚠️ Requires import  | ⚠️ Requires import         |
| API + Database join     | ✅ Direct                | ❌ Must export API  | ❌ Must export API         |
| Real-time streaming     | ✅ True streaming        | ⚠️ Buffering needed | ✅ Supports streaming      |
| Python processing       | ✅ Native                | ⚠️ Export/import    | ✅ PySpark API             |
| Zero infrastructure     | ✅ Yes                   | ✅ Yes              | ❌ Cluster needed          |
| GROUP BY / Aggregations | ❌ Not supported         | ✅ Full support     | ✅ Full support            |
| Maximum performance     | ⚠️ Moderate              | ✅ Very fast        | ✅ Very fast (distributed) |
| Memory efficiency       | ✅ Excellent             | ⚠️ Good             | ⚠️ Moderate                |
| Setup complexity        | ✅ Very low              | ✅ Low              | ❌ High                    |
| Best for                | Cross-system integration | Analytics           | Big data processing        |

---

## References

- [Best Use Cases Documentation](BEST_USE_CASES.md)
- [Performance Guide](PERFORMANCE.md)
- [Comprehensive Documentation](COMPREHENSIVE_DOCUMENTATION.md)
- [Library Documentation](LIBRARY_DOCUMENTATION.md)
