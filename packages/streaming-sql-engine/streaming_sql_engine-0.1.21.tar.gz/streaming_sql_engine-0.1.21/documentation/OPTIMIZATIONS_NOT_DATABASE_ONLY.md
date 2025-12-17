# Optimizations Are NOT Database-Only!

## ❌ Common Misconception

**"Optimizations are only for databases"** ← **WRONG!**

## ✅ Truth

**Optimizations work with ANY source that implements the protocol** - databases, APIs, files, anything!

---

## Why the Confusion?

The current code uses `is_database_source` flag, which makes it **seem** like optimizations are database-only. But they're not!

---

## Optimizations Work With:

### 1. ✅ Databases (PostgreSQL, MySQL, MongoDB)

```python
def db_source(dynamic_where=None, dynamic_columns=None):
    query = f"SELECT {', '.join(dynamic_columns)} FROM table"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"
    return execute(query)
```

### 2. ✅ REST APIs (If They Support Filtering/Field Selection)

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where  # API supports filtering!
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)  # API supports field selection!
    
    response = requests.get("https://api.com/products", params=params)
    for item in response.json():
        yield item
```

**Example APIs that support this:**
- GitHub API: `?filter=...&fields=...`
- Stripe API: `?filter=...&expand=...`
- Many REST APIs with query parameters

### 3. ✅ GraphQL APIs

```python
def graphql_source(dynamic_where=None, dynamic_columns=None):
    # Build GraphQL query with selected fields
    fields = dynamic_columns or ["*"]
    query = f"""
    {{
        products(filter: "{dynamic_where}") {{
            {' '.join(fields)}
        }}
    }}
    """
    response = requests.post("https://api.com/graphql", json={"query": query})
    for item in response.json()['data']['products']:
        yield item
```

### 4. ✅ File Formats (Parquet, CSV with filtering)

```python
def parquet_source(dynamic_where=None, dynamic_columns=None):
    import pyarrow.parquet as pq
    
    # Read only selected columns (column pruning)
    table = pq.read_table("data.parquet", columns=dynamic_columns)
    
    # Apply filter if supported (predicate pushdown)
    if dynamic_where:
        table = apply_filter(table, dynamic_where)
    
    for row in table.to_pylist():
        yield row
```

### 5. ✅ Any Custom Source

```python
def custom_source(dynamic_where=None, dynamic_columns=None):
    # Your custom data source
    # If it can filter and select columns, use optimizations!
    
    data = fetch_from_your_source()
    
    # Apply filter pushdown
    if dynamic_where:
        data = filter_data(data, dynamic_where)
    
    # Apply column pruning
    if dynamic_columns:
        data = select_columns(data, dynamic_columns)
    
    for row in data:
        yield row
```

---

## The Protocol is Source-Agnostic

**Protocol = Function signature pattern**

```python
def source(dynamic_where=None, dynamic_columns=None):
    # If your source can use these parameters → optimizations apply!
    ...
```

**It doesn't matter what your source is:**
- Database ✅
- API ✅
- File ✅
- Custom source ✅

**As long as it accepts these parameters and uses them, optimizations apply!**

---

## Current Code Problem

**Current code incorrectly assumes databases only:**

```python
# executor.py - WRONG assumption
if root_metadata.get('is_database_source'):  # ← Assumes only databases!
    apply_optimizations()
```

**This prevents optimizations from working with:**
- REST APIs that support filtering
- GraphQL APIs
- File formats
- Any non-database source

---

## Correct Approach: Protocol-Based

**Check function signature, not source type:**

```python
# executor.py - CORRECT approach
import inspect
sig = inspect.signature(source_fn)

# Check if source supports optimizations via protocol
supports_optimizations = (
    'dynamic_where' in sig.parameters or 
    'dynamic_columns' in sig.parameters
)

if supports_optimizations:  # Works with ANY source!
    apply_optimizations()
```

**Now optimizations work with:**
- ✅ Databases
- ✅ APIs
- ✅ Files
- ✅ Any source that implements protocol

---

## Real Examples

### Example 1: REST API with Optimizations

```python
def github_issues_source(dynamic_where=None, dynamic_columns=None):
    """GitHub API supports filtering and field selection."""
    params = {}
    
    # Filter pushdown: GitHub API supports filters
    if dynamic_where:
        # Convert SQL WHERE to GitHub filter format
        params['filter'] = convert_to_github_filter(dynamic_where)
    
    # Column pruning: GitHub API supports field selection
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.github.com/issues", params=params)
    for issue in response.json():
        yield issue

engine.register("issues", github_issues_source)
# Optimizations apply automatically! (Not a database!)
```

### Example 2: Parquet File with Optimizations

```python
def parquet_source(dynamic_where=None, dynamic_columns=None):
    """Parquet supports column selection and predicate pushdown."""
    import pyarrow.parquet as pq
    
    # Column pruning: Only read needed columns
    table = pq.read_table("large.parquet", columns=dynamic_columns)
    
    # Filter pushdown: Parquet supports predicate pushdown
    if dynamic_where:
        table = table.filter(convert_where_to_predicate(dynamic_where))
    
    for row in table.to_pylist():
        yield row

engine.register("data", parquet_source)
# Optimizations apply automatically! (Not a database!)
```

### Example 3: MongoDB (Not SQL Database, But Still Works)

```python
def mongo_source(dynamic_where=None, dynamic_columns=None):
    """MongoDB supports filters and projections."""
    collection = get_mongo_collection("products")
    
    # Filter pushdown: MongoDB filter
    filter_dict = {}
    if dynamic_where:
        filter_dict = parse_sql_to_mongo_filter(dynamic_where)
    
    # Column pruning: MongoDB projection
    projection = None
    if dynamic_columns:
        projection = {col: 1 for col in dynamic_columns}
    
    for doc in collection.find(filter_dict, projection):
        yield doc

engine.register("products", mongo_source)
# Optimizations apply automatically! (MongoDB is NoSQL, not SQL!)
```

---

## Summary

### ❌ Wrong Understanding

"Optimizations are only for databases"

### ✅ Correct Understanding

"Optimizations work with ANY source that implements the protocol"

**The protocol is:**
- Accept `dynamic_where` parameter → Filter pushdown
- Accept `dynamic_columns` parameter → Column pruning

**It doesn't matter if your source is:**
- SQL database (PostgreSQL, MySQL)
- NoSQL database (MongoDB)
- REST API
- GraphQL API
- File format (Parquet, CSV)
- Custom source

**As long as it can filter and select columns, optimizations apply!**

---

## Why Remove `is_database_source` Flag?

**Current (Wrong):**
```python
if is_database_source:  # Only databases get optimizations
    apply_optimizations()
```

**Future (Correct):**
```python
if function_accepts_protocol():  # ANY source can get optimizations
    apply_optimizations()
```

**Result:** More flexible, works with more sources, not limited to databases!

