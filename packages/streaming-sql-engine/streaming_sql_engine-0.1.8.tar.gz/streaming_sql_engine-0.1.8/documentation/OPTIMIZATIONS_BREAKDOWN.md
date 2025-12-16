# Optimizations Breakdown: Database-Specific vs. General

## Key Finding: **NONE of the optimizations are truly database-specific!**

They're currently tied to `is_database_source` flag, but they work with **any source** that implements the protocol.

---

## Current Optimizations

### 1. **Filter Pushdown** (Currently tied to `is_database_source`)

**What it does:**
- Pushes WHERE clause to the source instead of filtering in Python
- Reduces data transfer and processing

**Is it database-specific?** ❌ **NO!**

**Works with:**
- ✅ Databases (PostgreSQL, MySQL, MongoDB)
- ✅ REST APIs (if they support query parameters)
- ✅ GraphQL APIs (if they support filters)
- ✅ Some file formats (if you can filter while reading)
- ✅ Any source that can filter at source level

**Example - REST API:**
```python
def api_source(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where  # API supports filtering!
    
    response = requests.get("https://api.com/data", params=params)
    for item in response.json():
        yield item
```

**Example - MongoDB:**
```python
def mongo_source(dynamic_where=None, dynamic_columns=None):
    filter_dict = parse_where_to_mongo(dynamic_where) if dynamic_where else {}
    for doc in collection.find(filter_dict):
        yield doc
```

---

### 2. **Column Pruning** (Currently tied to `is_database_source`)

**What it does:**
- Only fetches columns needed for the query
- Reduces I/O and memory

**Is it database-specific?** ❌ **NO!**

**Works with:**
- ✅ Databases (SELECT specific columns)
- ✅ REST APIs (field selection: `?fields=id,name`)
- ✅ GraphQL APIs (field selection in query)
- ✅ Some file formats (columnar formats like Parquet)
- ✅ Any source that can select columns

**Example - REST API:**
```python
def api_source(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)  # API supports field selection!
    
    response = requests.get("https://api.com/data", params=params)
    for item in response.json():
        yield item
```

**Example - Parquet file:**
```python
def parquet_source(dynamic_where=None, dynamic_columns=None):
    import pyarrow.parquet as pq
    table = pq.read_table("data.parquet", columns=dynamic_columns)  # Column selection!
    for row in table.to_pylist():
        yield row
```

---

### 3. **Polars Vectorization** (General - works with any iterator)

**What it does:**
- Batch processing with SIMD operations
- 10-200x faster for large datasets

**Is it database-specific?** ❌ **NO!**

**Works with:**
- ✅ Any iterator (databases, files, APIs, custom sources)
- ✅ Automatically applied when Polars is available

**Example:**
```python
# Works with ANY source
def file_source():
    with open("data.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("data", file_source)
# Polars optimization applies automatically if available!
```

---

### 4. **Merge Joins** (General - works with sorted sources)

**What it does:**
- O(n+m) join when both sides are sorted
- Minimal memory usage

**Is it database-specific?** ❌ **NO!**

**Works with:**
- ✅ Any sorted source (databases with ORDER BY, sorted files, sorted APIs)
- ✅ Controlled by `ordered_by` metadata

**Example:**
```python
# Works with sorted file
def sorted_file_source():
    # File is sorted by id
    with open("sorted_data.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("data", sorted_file_source, ordered_by="id")
# Merge join applies automatically!
```

---

### 5. **Memory-Mapped Joins** (File-specific, not database-specific)

**What it does:**
- Uses mmap for file-based joins
- 90-99% memory reduction

**Is it database-specific?** ❌ **NO!** (It's file-specific)

**Works with:**
- ✅ JSONL files
- ✅ Any file-based source with `filename` metadata

**Example:**
```python
def jsonl_source():
    with open("large_file.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("data", jsonl_source, filename="large_file.jsonl")
# Mmap join applies automatically!
```

---

## Summary Table

| Optimization | Database-Specific? | Works With | Current Status |
|-------------|-------------------|------------|----------------|
| **Filter Pushdown** | ❌ NO | Any source with filtering capability | Tied to `is_database_source` flag |
| **Column Pruning** | ❌ NO | Any source with column selection | Tied to `is_database_source` flag |
| **Polars Vectorization** | ❌ NO | Any iterator | ✅ Already general |
| **Merge Joins** | ❌ NO | Any sorted source | ✅ Already general (via `ordered_by`) |
| **Mmap Joins** | ❌ NO | File-based sources | ✅ Already general (via `filename`) |

---

## The Problem

**Current code incorrectly assumes optimizations are database-specific:**

```python
# executor.py - WRONG assumption
if root_metadata.get('is_database_source') and (root_required_columns or pushable_where_sql):
    # Apply optimizations
```

**This prevents optimizations from working with:**
- REST APIs that support filtering
- GraphQL APIs with field selection
- Parquet/columnar files
- Any non-database source that could benefit

---

## The Solution: Protocol-Based Detection

**Remove `is_database_source` flag, use function signature detection:**

```python
# executor.py - CORRECT approach
import inspect
sig = inspect.signature(root_source_fn)

# Check if source supports optimizations via protocol
supports_filter_pushdown = 'dynamic_where' in sig.parameters
supports_column_pruning = 'dynamic_columns' in sig.parameters

if (supports_filter_pushdown or supports_column_pruning) and (root_required_columns or pushable_where_sql):
    # Apply optimizations - works with ANY source that implements protocol!
    ...
```

---

## Examples: Non-Database Sources Using Optimizations

### REST API with Filter Pushdown

```python
def rest_api_source(dynamic_where=None, dynamic_columns=None):
    """REST API that supports query parameters."""
    params = {}
    if dynamic_where:
        # Convert SQL WHERE to API filter format
        params['filter'] = convert_sql_to_api_filter(dynamic_where)
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.com/products", params=params)
    for item in response.json():
        yield item

engine.register("products", rest_api_source)  # Optimizations apply!
```

### GraphQL API with Field Selection

```python
def graphql_source(dynamic_where=None, dynamic_columns=None):
    """GraphQL API with field selection."""
    # Build GraphQL query with selected fields
    fields = dynamic_columns or ["*"]
    query = f"""
    {{
        products {{
            {' '.join(fields)}
        }}
    }}
    """
    
    response = requests.post("https://api.com/graphql", json={"query": query})
    for item in response.json()['data']['products']:
        yield item

engine.register("products", graphql_source)  # Column pruning applies!
```

### Parquet File with Column Pruning

```python
def parquet_source(dynamic_where=None, dynamic_columns=None):
    """Parquet file with column selection."""
    import pyarrow.parquet as pq
    
    # Read only selected columns
    table = pq.read_table("data.parquet", columns=dynamic_columns)
    
    # Apply filter if supported (some formats support predicate pushdown)
    if dynamic_where:
        # Filter in memory (or use predicate pushdown if available)
        table = apply_filter(table, dynamic_where)
    
    for row in table.to_pylist():
        yield row

engine.register("data", parquet_source)  # Column pruning applies!
```

---

## Conclusion

**Answer: NONE of the optimizations are database-specific!**

They're just **source capabilities** that can be implemented by:
- Databases ✅
- REST APIs ✅
- GraphQL APIs ✅
- File formats ✅
- Any custom source ✅

**The protocol-based approach enables optimizations for ANY source that implements it, not just databases.**

This is why removing `is_database_source` and using pure protocol detection is the right approach!

