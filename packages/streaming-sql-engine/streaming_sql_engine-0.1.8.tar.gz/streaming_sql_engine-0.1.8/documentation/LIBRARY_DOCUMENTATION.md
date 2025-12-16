# Streaming SQL Engine - Library Documentation

## Purpose

The Streaming SQL Engine is a lightweight Python library that executes SQL queries with joins in a **streaming, row-by-row fashion** without loading entire tables into memory. It enables SQL querying across heterogeneous data sources (databases, files, APIs) with efficient memory usage and flexible execution strategies.

### Key Design Goals

- **Memory Efficiency**: Process large datasets without materializing full tables
- **Source Agnostic**: Query across databases, files, APIs, and custom data sources
- **Streaming Execution**: Yield results incrementally as they're produced
- **Performance**: Optimize through column pruning, filter pushdown, and vectorized operations

---

## Data Flow

### High-Level Flow

```
SQL Query → Parser → Logical Plan → Optimizer → Executor → Results (Generator)
```

### Detailed Execution Pipeline

1. **SQL Parsing** (`parser.py`)

   - SQL string → Abstract Syntax Tree (AST) using `sqlglot`
   - Validates supported constructs (SELECT, JOIN, WHERE)
   - Rejects unsupported features (GROUP BY, ORDER BY, aggregations)

2. **Logical Planning** (`planner.py`)

   - AST → Logical execution plan
   - Extracts: root table, joins, WHERE clause, projections
   - Identifies table aliases and join conditions

3. **Optimization** (`optimizer.py`)

   - **Column Pruning**: Identifies which columns are needed from each table
   - **Filter Pushdown**: Determines which WHERE conditions can be pushed to data sources
   - Annotates plan with optimization metadata

4. **Execution** (`executor.py` or `jsonl_executor.py`)
   - Builds iterator pipeline:
     ```
     ScanIterator → FilterIterator → JoinIterators → ProjectIterator
     ```
   - Each iterator processes rows incrementally
   - Results are yielded as generators (not buffered)

### Iterator Pipeline Example

For query: `SELECT users.name FROM users JOIN orders ON users.id = orders.user_id WHERE users.active = 1`

```
ScanIterator(users)
  → FilterIterator(WHERE active=1)
    → LookupJoinIterator(orders, build index on orders.user_id)
      → ProjectIterator(SELECT name)
        → Results (generator)
```

---

## Capabilities

### Supported SQL Features

**SELECT**

- Column selection with table qualification (`users.name`)
- Column aliasing (`SELECT name AS user_name`)
- Multiple columns in projection

**FROM**

- Single table with optional alias
- Table name resolution from registered sources

**JOIN**

- **INNER JOIN**: Equality joins only (`ON left.key = right.key`)
- **LEFT JOIN**: Preserves all left rows, NULLs for unmatched right rows
- Multiple sequential joins
- Join key must be equality condition

**WHERE**

- Comparisons: `=`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean logic: `AND`, `OR`, `NOT`
- NULL checks: `IS NULL`, `IS NOT NULL`
- IN clauses: `column IN (value1, value2, ...)`
- Table-qualified columns: `users.id = 1`

### Execution Modes

1. **Standard Mode** (default)

   - In-memory iterator pipeline
   - Supports Polars acceleration (vectorized operations)
   - Supports memory-mapped joins for file sources

2. **JSONL Mode** (`use_jsonl_mode=True`)
   - Exports tables to JSONL files, then merges
   - Lower CPU usage for complex queries
   - Useful when intermediate results exceed memory

### Performance Optimizations

1. **Column Pruning**

   - Only reads columns needed for query
   - Reduces I/O and memory for wide tables
   - Automatic based on SELECT and WHERE clauses

2. **Filter Pushdown**

   - Pushes WHERE conditions to database sources
   - Reduces data transfer from database
   - Only for conditions referencing root table

3. **Join Algorithm Selection**

   - **Merge Join**: When both sides sorted by join key (O(n+m))
   - **Lookup Join**: Hash index on smaller table (O(n\*m) worst case)
   - **Polars Join**: Vectorized batch processing (10-200x faster)
   - **Mmap Join**: Memory-mapped file access (90-99% memory reduction)

4. **Polars Acceleration** (optional)
   - Vectorized filtering and projection
   - SIMD-optimized operations
   - Batch processing (10,000 rows at a time)

---

## Supported Data Sources

### Database Sources

**PostgreSQL**

- Connection pooling via `PostgreSQLPool`
- Server-side cursors for streaming
- Filter pushdown and column pruning support

**MySQL**

- Connection pooling via `MySQLPool`
- Batch fetching for streaming
- Filter pushdown and column pruning support

**MongoDB**

- Connection via `MongoPool`
- Collection queries with filters and projections
- Document streaming

### File Sources

**JSONL Files**

- Line-by-line reading
- Memory-mapped joins when `filename` provided
- Supports large files without full memory load

**CSV Files** (via custom source functions)

- Any file format via iterator functions

### API Sources

**REST APIs** (via custom source functions)

- Any HTTP API via iterator functions
- Supports pagination and authentication

### Custom Sources

Any Python function returning an iterator of dictionaries:

```python
def custom_source():
    return iter([{"col1": val1, "col2": val2}, ...])
```

---

## Data Source Combinations

### Supported Combinations

✅ **Database + Database**: PostgreSQL ↔ MySQL joins  
✅ **Database + File**: Database table JOIN JSONL file  
✅ **File + File**: JSONL file JOIN JSONL file  
✅ **API + Database**: REST API JOIN database table  
✅ **API + File**: REST API JOIN JSONL file  
✅ **Any combination**: All sources are treated uniformly as iterators

### Cross-Source Join Example

```python
# PostgreSQL table + JSONL file + MongoDB collection
engine.register("products", create_table_source(pg_pool, "products"))
engine.register("images", lambda: load_jsonl("images.jsonl"), filename="images.jsonl")
engine.register("specs", create_mongo_collection_source(mongo_pool, "specs"))

query = """
    SELECT products.name, images.url, specs.description
    FROM products
    JOIN images ON products.id = images.product_id
    JOIN specs ON products.id = specs.product_id
"""
```

---

## Typical Usage Scenarios

### 1. Database Query with Joins

**Use Case**: Query multiple PostgreSQL tables with joins

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source

pool = create_pool_from_env()
engine = Engine(debug=True)

engine.register("users", create_table_source(pool, "users"), is_database_source=True)
engine.register("orders", create_table_source(pool, "orders"), is_database_source=True)

for row in engine.query("""
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
    WHERE users.active = 1
"""):
    print(row)
```

**Benefits**: Filter pushdown reduces database load, column pruning reduces transfer

### 2. File-Based Data Processing

**Use Case**: Join large JSONL files without loading into memory

```python
engine = Engine(use_jsonl_mode=True)  # Lower CPU for large files

engine.register("products", lambda: load_jsonl("products.jsonl"), filename="products.jsonl")
engine.register("images", lambda: load_jsonl("images.jsonl"), filename="images.jsonl")

for row in engine.query("""
    SELECT products.name, images.url
    FROM products
    JOIN images ON products.id = images.product_id
"""):
    process(row)
```

**Benefits**: Memory-mapped joins use 90-99% less memory than in-memory joins

### 3. Multi-Source Data Integration

**Use Case**: Combine data from databases, files, and APIs

```python
engine = Engine()

# Database source
engine.register("users", create_table_source(pg_pool, "users"))

# File source
engine.register("logs", lambda: load_jsonl("logs.jsonl"))

# API source
engine.register("events", lambda: fetch_api_events())

for row in engine.query("""
    SELECT users.name, logs.action, events.timestamp
    FROM users
    JOIN logs ON users.id = logs.user_id
    JOIN events ON users.id = events.user_id
    WHERE logs.date = '2024-01-01'
"""):
    analyze(row)
```

**Benefits**: Unified SQL interface across heterogeneous sources

### 4. ETL Pipeline

**Use Case**: Transform and join data during extraction

```python
engine = Engine(use_jsonl_mode=True)  # Export to JSONL for downstream processing

# Register sources
engine.register("source1", source1_iterator)
engine.register("source2", source2_iterator)

# Execute query and write results
with open("output.jsonl", "w") as f:
    for row in engine.query("SELECT ... JOIN ..."):
        f.write(json.dumps(row) + "\n")
```

**Benefits**: Streaming execution prevents memory overflow on large datasets

---

## Module Responsibilities

### Core Modules

**`engine.py`** - Public API

- `Engine` class: Main interface for users
- `register()`: Register table sources with metadata
- `query()`: Execute SQL and return generator
- Coordinates parsing, planning, and execution

**`parser.py`** - SQL Parsing

- `parse_sql()`: Converts SQL string to AST
- `_validate_query()`: Ensures only supported constructs
- Uses `sqlglot` for dialect-agnostic parsing

**`planner.py`** - Logical Planning

- `build_logical_plan()`: Converts AST to logical plan
- Extracts tables, joins, WHERE, projections
- Creates `LogicalPlan` dataclass

**`optimizer.py`** - Query Optimization

- `analyze_required_columns()`: Column pruning analysis
- `analyze_filter_pushdown()`: Filter pushdown analysis
- `expression_to_sql_string()`: Converts expressions to SQL for pushdown

**`executor.py`** - Standard Execution

- `execute_plan()`: Builds iterator pipeline
- `_build_join_iterator()`: Selects optimal join algorithm
- Integrates Polars and mmap optimizations

**`jsonl_executor.py`** - JSONL-Based Execution

- `execute_plan_jsonl()`: Export-then-merge strategy
- `_export_table_to_jsonl()`: Writes tables to JSONL
- `_merge_jsonl_files()`: Joins JSONL files
- Lower CPU usage for complex queries

### Operator Modules

**`operators.py`** - Iterator Operators

- `ScanIterator`: Reads from source functions
- `FilterIterator`: Applies WHERE conditions
- `ProjectIterator`: Applies SELECT projections
- `LookupJoinIterator`: Hash-based joins
- `MergeJoinIterator`: Sorted merge joins

**`polars_operators.py`** - Polars Acceleration (Optional)

- `PolarsLookupJoinIterator`: Vectorized joins
- `PolarsBatchFilterIterator`: Vectorized filtering
- `PolarsBatchProjectIterator`: Vectorized projection
- Requires `polars` package

**`operators_mmap.py`** - Memory-Mapped Joins (Optional)

- `MmapLookupJoinIterator`: File-based joins with mmap
- 90-99% memory reduction for large files
- Requires file path in source metadata

### Supporting Modules

**`evaluator.py`** - Expression Evaluation

- `evaluate_expression()`: Evaluates SQL expressions against rows
- Handles comparisons, boolean logic, NULL checks, IN clauses
- Optimized with type caching for performance

**`db_connector.py`** - Database Integration

- `PostgreSQLPool`, `MySQLPool`, `MongoPool`: Connection pools
- `create_table_source()`: Creates database source functions
- `stream_query()`: Streams rows from database queries
- `create_mongo_collection_source()`: MongoDB collection sources
- Supports filter pushdown and column pruning for databases

---

## Architecture and Design Influences

### Design Principles

1. **Iterator-Based Streaming**

   - Inspired by Python's generator pattern
   - Enables processing datasets larger than memory
   - Lazy evaluation: compute only what's needed

2. **Pipeline Architecture**

   - Similar to database query executors (PostgreSQL, MySQL)
   - Each operator transforms iterator → iterator
   - Enables composition and optimization

3. **Source Abstraction**
   - All sources are functions returning iterators
   - Uniform interface regardless of underlying storage
   - Enables cross-source joins

### Architectural Decisions

**Why Streaming?**

- Memory constraints: Can't load entire tables
- Early results: Yield rows as soon as available
- Scalability: Handle datasets of any size

**Why Iterator Pipeline?**

- Composability: Operators chain naturally
- Testability: Each operator independently testable
- Flexibility: Easy to add new operators

**Why Multiple Execution Modes?**

- **Standard mode**: Fastest for in-memory operations
- **JSONL mode**: Lower CPU for complex queries, handles memory pressure
- Trade-off: Standard mode faster, JSONL mode more memory-efficient

**Why Multiple Join Algorithms?**

- **Merge join**: O(n+m) when sorted, minimal memory
- **Lookup join**: General-purpose, O(n\*m) worst case
- **Polars join**: 10-200x faster for large datasets
- **Mmap join**: 90-99% memory reduction for files
- Selection based on source capabilities and data characteristics

**Why Column Pruning?**

- Reduces I/O for wide tables
- Reduces memory for intermediate results
- Critical for database sources (less data transfer)

**Why Filter Pushdown?**

- Reduces data transfer from databases
- Leverages database indexes
- Only for root table (simplifies implementation)

### Trade-offs

**Memory vs. Speed**

- Lookup joins: Fast but require building index (memory)
- Merge joins: Low memory but require sorted data
- JSONL mode: Lower memory but disk I/O overhead

**Simplicity vs. Features**

- No GROUP BY/aggregations: Keeps implementation simple
- No subqueries: Avoids complexity explosion
- Equality joins only: Simplifies join algorithms

**Flexibility vs. Performance**

- Source abstraction enables any data source
- But prevents some optimizations (e.g., database-specific)
- Balance: Optimize common cases (databases, files) while supporting custom sources

---

## Summary

The Streaming SQL Engine provides a **unified SQL interface** for querying heterogeneous data sources with **memory-efficient streaming execution**. Its architecture prioritizes:

- **Memory efficiency** through streaming and optimizations
- **Source flexibility** through iterator abstraction
- **Performance** through multiple execution strategies
- **Simplicity** through focused feature set

The library is designed for scenarios where:

- Datasets are too large for in-memory processing
- Data spans multiple sources (databases, files, APIs)
- Memory usage must be minimized
- Results can be processed incrementally

By combining SQL parsing, query optimization, and flexible execution strategies, it enables complex data integration workflows without the overhead of full database systems.
