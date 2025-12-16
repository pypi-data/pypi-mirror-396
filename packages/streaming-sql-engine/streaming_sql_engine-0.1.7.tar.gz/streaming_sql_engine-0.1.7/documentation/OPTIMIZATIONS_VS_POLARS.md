# Optimizations vs Polars: What They Do and How They Work

## Two Different Types of Optimizations

### 1. **Protocol-Based Optimizations** (Filter Pushdown + Column Pruning)

- Work **at the source level** (before data enters engine)
- Reduce data transfer from source
- Protocol-based (function signature detection)

### 2. **Polars Optimizations** (Vectorized Operations)

- Work **inside the engine** (after data is loaded)
- Speed up processing with SIMD operations
- Automatic (if Polars installed)

**They are SEPARATE and work together!**

---

## Protocol-Based Optimizations: What They Do

### Filter Pushdown (`dynamic_where`)

**What it does:** Pushes WHERE clause to source, so source filters before sending data.

**How it works:**

```python
# Query
query = "SELECT * FROM users WHERE users.id > 100"

# Step 1: Engine analyzes query
pushable_where = "users.id > 100"  # Can push to users table

# Step 2: Engine checks protocol
def users_source(dynamic_where=None, dynamic_columns=None):
    # Engine detects: function accepts dynamic_where ✅
    ...

# Step 3: Engine calls source with optimization
users_source(dynamic_where="users.id > 100")

# Step 4: Source uses WHERE clause
def users_source(dynamic_where=None, dynamic_columns=None):
    query = "SELECT * FROM users"
    if dynamic_where:  # "users.id > 100"
        query += f" WHERE {dynamic_where}"  # Adds WHERE clause
    # Final: "SELECT * FROM users WHERE users.id > 100"
    return execute(query)  # Database filters → only 500 rows sent

# Result: Only filtered rows come to engine (not all 1,000,000 rows!)
```

**Benefits:**

- ✅ Less data transferred (source filters first)
- ✅ Faster (source uses indexes)
- ✅ Less memory (fewer rows in engine)

### Column Pruning (`dynamic_columns`)

**What it does:** Only fetches columns needed for query, not all columns.

**How it works:**

```python
# Query
query = "SELECT users.name FROM users JOIN orders ON users.id = orders.user_id"

# Step 1: Engine analyzes query
required_columns = {
    "users": {"id", "name"},      # Only need id and name
    "orders": {"user_id", "total"} # Only need user_id and total
}

# Step 2: Engine checks protocol
def users_source(dynamic_where=None, dynamic_columns=None):
    # Engine detects: function accepts dynamic_columns ✅
    ...

# Step 3: Engine calls source with optimization
users_source(dynamic_columns=["id", "name"])

# Step 4: Source uses column list
def users_source(dynamic_where=None, dynamic_columns=None):
    columns = dynamic_columns or ["*"]  # ["id", "name"]
    query = f"SELECT {', '.join(columns)} FROM users"
    # Final: "SELECT id, name FROM users"
    return execute(query)  # Database only selects id, name

# Result: Only needed columns come to engine (not all 20 columns!)
```

**Benefits:**

- ✅ Less data transferred (only needed columns)
- ✅ Less memory (smaller rows)
- ✅ Faster I/O (less data to read)

---

## How Protocol Detection Works

### Step-by-Step Process

```python
# 1. User registers source
def my_source(dynamic_where=None, dynamic_columns=None):
    # Source implementation
    ...

engine.register("table", my_source)

# 2. Engine checks function signature
import inspect
sig = inspect.signature(my_source)
params = list(sig.parameters.keys())
# params = ['dynamic_where', 'dynamic_columns']

# 3. Engine detects protocol
has_where = 'dynamic_where' in params      # ✅ True
has_columns = 'dynamic_columns' in params  # ✅ True
supports_optimizations = has_where or has_columns  # ✅ True

# 4. When query executes, engine applies optimizations
if supports_optimizations:
    # Call source with optimization parameters
    source_iterator = my_source(
        dynamic_where="id > 100",      # Filter pushdown
        dynamic_columns=["id", "name"]  # Column pruning
    )
else:
    # No optimizations, call normally
    source_iterator = my_source()
```

---

## Polars: What It Does (Separate from Protocol Optimizations)

### Polars = Vectorized Batch Processing

**What it does:** Processes rows in batches using SIMD operations (10-200x faster).

**How it works:**

```python
# Query
query = "SELECT * FROM users JOIN orders ON users.id = orders.user_id"

# Step 1: Data already loaded (protocol optimizations already applied)
# Protocol optimizations reduced data: 1M rows → 500 rows

# Step 2: Polars processes batches
# Collects rows into batches (10,000 rows)
batch = [row1, row2, ..., row10000]

# Step 3: Convert to Polars DataFrame
df = pl.DataFrame(batch)

# Step 4: Vectorized operations (SIMD-accelerated)
result_df = df.join(...)  # Fast vectorized join

# Step 5: Convert back to rows
for row in result_df.to_dicts():
    yield row
```

**Benefits:**

- ✅ Fast (SIMD operations)
- ✅ Batch processing (efficient)
- ✅ Works with any iterator

**When it's used:**

- Joins (PolarsLookupJoinIterator)
- Filtering (planned - PolarsBatchFilterIterator)
- Projection (PolarsBatchProjectIterator)

---

## How They Work Together

### Complete Flow

```
1. Query: "SELECT users.name FROM users JOIN orders WHERE users.id > 100"

2. PROTOCOL OPTIMIZATIONS (at source level):
   ├─ Filter Pushdown: users_source(dynamic_where="id > 100")
   │  └─ Database filters → 1M rows → 500 rows
   │
   └─ Column Pruning: users_source(dynamic_columns=["id", "name"])
      └─ Database selects → 20 columns → 2 columns

   Result: 500 rows × 2 columns (instead of 1M rows × 20 columns)

3. Data enters engine (already optimized by protocol)

4. POLARS OPTIMIZATIONS (inside engine):
   ├─ Batch processing: Collect 10,000 rows into batches
   ├─ Vectorized join: Fast SIMD operations
   └─ Yield results incrementally

   Result: Fast processing of already-reduced data

5. Final output: Optimized results
```

---

## Key Differences

| Feature        | Protocol Optimizations          | Polars                      |
| -------------- | ------------------------------- | --------------------------- |
| **Where**      | At source level                 | Inside engine               |
| **When**       | Before data enters engine       | After data is loaded        |
| **What**       | Filter pushdown, column pruning | Vectorized batch processing |
| **How**        | Function signature protocol     | Automatic (if installed)    |
| **Benefit**    | Less data transferred           | Faster processing           |
| **Works with** | Any source (DB, API, file)      | Any iterator                |

---

## Example: Both Working Together

### Without Optimizations

```python
# 1. Source fetches everything
def source():
    return execute("SELECT * FROM users")  # 1M rows × 20 columns

# 2. Engine filters in Python (slow)
for row in source():
    if row['id'] > 100:  # Filtering in Python
        # Process row

# 3. Engine joins in Python (slow)
# Dict-based join (slow)

# Result: Slow, high memory
```

### With Protocol Optimizations Only

```python
# 1. Source uses protocol optimizations
def source(dynamic_where=None, dynamic_columns=None):
    query = f"SELECT {', '.join(dynamic_columns)} FROM users"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"
    return execute(query)  # 500 rows × 2 columns

# 2. Engine filters (less data now)
for row in source(dynamic_where="id > 100", dynamic_columns=["id", "name"]):
    # Process row (already filtered!)

# 3. Engine joins in Python (faster - less data)
# Dict-based join (faster because less data)

# Result: Faster, less memory (but still Python-based)
```

### With Protocol + Polars Optimizations

```python
# 1. Source uses protocol optimizations (same as above)
def source(dynamic_where=None, dynamic_columns=None):
    query = f"SELECT {', '.join(dynamic_columns)} FROM users"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"
    return execute(query)  # 500 rows × 2 columns

# 2. Engine uses Polars for processing
# Polars processes batches with SIMD (very fast!)

# Result: Fastest, least memory
```

---

## Protocol Optimizations: Detailed Example

### Example 1: Database Source

```python
def db_source(dynamic_where=None, dynamic_columns=None):
    """Database source with protocol optimizations."""

    # Build query with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""

    query = f"SELECT {', '.join(columns)} FROM products"
    if where:
        query += f" WHERE {where}"

    # Execute optimized query
    cursor = execute(query)
    for row in cursor:
        yield dict(row)

# Engine calls:
# db_source(dynamic_where="price > 100", dynamic_columns=["id", "name", "price"])
# Database executes: "SELECT id, name, price FROM products WHERE price > 100"
# Only filtered, pruned data comes to engine!
```

### Example 2: REST API Source

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    """REST API source with protocol optimizations."""

    params = {}

    # Filter pushdown: API supports filtering
    if dynamic_where:
        params['filter'] = convert_sql_to_api_filter(dynamic_where)

    # Column pruning: API supports field selection
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)

    # Call API with optimizations
    response = requests.get("https://api.com/products", params=params)
    for item in response.json():
        yield item

# Engine calls:
# api_source(dynamic_where="price > 100", dynamic_columns=["id", "name", "price"])
# API call: GET /products?filter=price>100&fields=id,name,price
# Only filtered, pruned data comes to engine!
```

### Example 3: File Source (No Protocol)

```python
def file_source():
    """Simple file source - no protocol optimizations."""
    with open("products.jsonl") as f:
        for line in f:
            yield json.loads(line)

# Engine calls:
# file_source()  # No optimization parameters
# All data comes to engine, filtering happens in Python
```

---

## Polars: Detailed Example

### How Polars Works in Engine

```python
# executor.py - Polars join

# 1. Right table loaded (protocol optimizations already applied)
right_rows = []
for row in right_source():  # Already optimized by protocol
    right_rows.append(row)

# 2. Convert to Polars DataFrame
right_df = pl.DataFrame(right_rows)

# 3. Process left table in batches
left_batch = []
for left_row in left_source():
    left_batch.append(left_row)

    if len(left_batch) >= 10000:
        # Convert batch to DataFrame
        left_df = pl.DataFrame(left_batch)

        # Vectorized join (SIMD-accelerated)
        result_df = left_df.join(right_df, ...)

        # Yield results
        for row in result_df.to_dicts():
            yield row

        left_batch = []
```

**Polars benefits:**

- ✅ SIMD operations (parallel processing)
- ✅ Batch processing (efficient memory use)
- ✅ Vectorized operations (faster than Python loops)

---

## Summary

### Protocol-Based Optimizations

**What:** Filter pushdown + Column pruning  
**Where:** At source level (before data enters engine)  
**How:** Function signature protocol (`dynamic_where`, `dynamic_columns`)  
**Benefit:** Less data transferred, less memory  
**Works with:** Any source (database, API, file, custom)

### Polars Optimizations

**What:** Vectorized batch processing  
**Where:** Inside engine (after data is loaded)  
**How:** Automatic (if Polars installed)  
**Benefit:** Faster processing (SIMD operations)  
**Works with:** Any iterator

### They Work Together

1. **Protocol optimizations** reduce data at source
2. **Polars optimizations** process reduced data faster
3. **Result:** Fastest, most memory-efficient

**They are SEPARATE but COMPLEMENTARY!**
