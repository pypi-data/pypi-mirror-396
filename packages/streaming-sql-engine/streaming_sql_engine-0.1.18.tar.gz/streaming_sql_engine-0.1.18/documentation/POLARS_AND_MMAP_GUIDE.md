# Polars and Mmap Index Guide

## How Polars is Used

### 1. **Automatic (Default Behavior)**

Polars is used automatically when available. You don't need to do anything special!

```python
from streaming_sql_engine import Engine

# Polars is enabled by default
engine = Engine()  # use_polars=True by default

# If Polars is installed, it's used automatically
# If not installed, falls back to Python iterators
```

**What Polars does:**

- **Joins**: 10-200x faster than Python dict-based joins
- **Filtering**: Vectorized WHERE clause evaluation (SIMD-accelerated)
- **Projection**: Fast SELECT column operations

### 2. **Where Polars is Applied**

#### A. **Join Operations** (`PolarsLookupJoinIterator`)

```python
# Engine automatically uses Polars for joins if:
# 1. Polars is installed
# 2. use_polars=True (default)
# 3. Right table is large enough (>10,000 rows threshold)

# Example:
engine.register("products", products_source)
engine.register("images", images_source)

# When joining, engine checks:
# - Is Polars available? ✅
# - Is right table large? ✅
# → Uses PolarsJoinIterator automatically
```

**How it works:**

1. Loads right table into Polars DataFrame (in-memory)
2. Processes left table in batches (10,000 rows)
3. Performs vectorized join using Polars
4. Yields results incrementally

**Performance:** 10-200x faster than Python dict joins

#### B. **Filtering** (`PolarsBatchFilterIterator`)

```python
# For WHERE clauses, Polars processes rows in batches
query = "SELECT * FROM products WHERE price > 100"

# Engine automatically:
# 1. Collects rows into batches (10,000 rows)
# 2. Converts batch to Polars DataFrame
# 3. Applies filter using vectorized operations
# 4. Yields filtered rows
```

**Note:** Currently `PolarsBatchFilterIterator` is not fully implemented (raises `NotImplementedError`), so filtering falls back to Python.

#### C. **Projection** (`PolarsBatchProjectIterator`)

```python
# For SELECT operations, Polars processes in batches
query = "SELECT name, price FROM products"

# Engine automatically:
# 1. Collects rows into batches
# 2. Converts to Polars DataFrame
# 3. Selects columns using vectorized operations
# 4. Yields projected rows
```

### 3. **Disabling Polars**

If you want to disable Polars (use pure Python):

```python
engine = Engine(use_polars=False)
```

**When to disable:**

- Debugging iterator behavior
- Memory constraints (Polars loads right table into memory)
- Small datasets (overhead not worth it)

---

## Mmap Index: Do You Need It?

### **Short Answer: Only if you have VERY large files (>100MB) and memory constraints**

### What is Mmap Index?

**Memory-mapped file index** - Instead of loading full rows into memory, stores **file positions** and reads rows on-demand from disk.

**Memory savings:** 90-99% reduction

### How It Works

```
Normal Join (In-Memory):
┌─────────────────────────────────┐
│ Load ALL rows into memory       │
│ {id: 1, name: "A", ...}         │  ← Full objects
│ {id: 2, name: "B", ...}         │
│ ...                              │
│ Memory: 1GB for 1M rows          │
└─────────────────────────────────┘

Mmap Join (Position-Based):
┌─────────────────────────────────┐
│ Store ONLY positions            │
│ {id: 1: [0, 1024, 2048]}        │  ← File positions (8 bytes each)
│ {id: 2: [3072]}                  │
│ ...                              │
│ Memory: 10MB for 1M rows        │  ← 99% reduction!
│                                  │
│ Read rows on-demand from disk   │
└─────────────────────────────────┘
```

### When to Use Mmap

✅ **Use mmap when:**

- File-based sources (JSONL files)
- Very large files (>100MB)
- Memory constraints (can't load full table)
- Right table in join is large

❌ **Don't use mmap when:**

- Database sources (databases handle their own memory)
- Small files (<10MB) - overhead not worth it
- API sources (not file-based)
- Memory is not a concern

### How to Enable Mmap

**Option 1: Provide filename when registering source**

```python
def jsonl_source():
    with open("large_file.jsonl") as f:
        for line in f:
            yield json.loads(line)

# Register with filename - enables mmap automatically
engine.register(
    "products",
    jsonl_source,
    filename="large_file.jsonl"  # ← This enables mmap!
)
```

**Option 2: Engine automatically selects mmap**

The engine prioritizes mmap over Polars for large files:

```python
# Engine's join selection priority:
# 1. Merge join (if sorted) - O(n+m), minimal memory
# 2. Mmap join (if filename provided) - Low memory, fast
# 3. Polars join (if available) - Fast, but uses memory
# 4. Python join (fallback) - Slow, uses memory
```

### Mmap vs Polars

| Feature      | Mmap                            | Polars                         |
| ------------ | ------------------------------- | ------------------------------ |
| **Memory**   | ✅ Very low (positions only)    | ❌ High (loads full DataFrame) |
| **Speed**    | ✅ Fast (mmap is efficient)     | ✅✅ Very fast (SIMD)          |
| **Use Case** | Large files, memory constraints | Large datasets, speed priority |
| **Requires** | Filename metadata               | Polars installed               |

**Engine's decision logic:**

```python
# In executor.py
if filename_provided:
    use_mmap()  # Lowest memory
elif polars_available and table_large:
    use_polars()  # Fastest
else:
    use_python()  # Fallback
```

### Mmap Index Implementation

The `mmap_index.py` file provides:

1. **`MmapPositionIndex`** - Position-based index

   - Stores file positions instead of full objects
   - Reads rows on-demand using memory-mapped files
   - Can use Polars for faster index building

2. **Index Building**
   - **With Polars**: Faster grouping (SIMD-accelerated)
   - **Without Polars**: Standard Python grouping

**Example:**

```python
from mmap_index import MmapPositionIndex

# Build index for a JSONL file
index = MmapPositionIndex(
    filename="products.jsonl",
    key_column="product_id",
    use_polars=True  # Faster index building
)

# Get rows for a key (reads from disk on-demand)
rows = index.get_rows(product_id=123)
```

---

## Practical Examples

### Example 1: Small Dataset (No Mmap Needed)

```python
# Small file (<10MB) - use Polars or Python
engine = Engine(use_polars=True)

def small_source():
    with open("small.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("data", small_source)
# Engine uses Polars join (fast, memory OK for small files)
```

### Example 2: Large File (Use Mmap)

```python
# Large file (>100MB) - use mmap to save memory
engine = Engine(use_polars=True)  # Still use Polars for other operations

def large_source():
    with open("huge_file.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register(
    "data",
    large_source,
    filename="huge_file.jsonl"  # Enables mmap!
)
# Engine uses mmap join (low memory) for this table
# But still uses Polars for filtering/projection
```

### Example 3: Database Source (No Mmap)

```python
# Databases handle their own memory - no mmap needed
def db_source(dynamic_where=None, dynamic_columns=None):
    # Database streaming - no file involved
    ...

engine.register("products", db_source)
# Engine uses Polars join (if available) or Python join
# No mmap (not file-based)
```

---

## Summary

### Polars Usage

✅ **Automatic** - Enabled by default  
✅ **Optional** - Falls back to Python if not installed  
✅ **Fast** - 10-200x speedup for joins  
✅ **Used for** - Joins, filtering (planned), projection

**You don't need to do anything** - just install Polars:

```bash
pip install polars
```

### Mmap Index

✅ **Optional** - Only for large file-based sources  
✅ **Memory-efficient** - 90-99% memory reduction  
✅ **Automatic** - Enabled when `filename` provided  
✅ **Use when** - Large files (>100MB) with memory constraints

**You only need it if:**

- You have very large JSONL files
- Memory is constrained
- Right table in join is large

**Otherwise, Polars or Python joins work fine!**

---

## Decision Tree

```
Do you have file-based sources?
├─ NO → Use Polars or Python (no mmap)
│
└─ YES → Is file >100MB?
    ├─ NO → Use Polars or Python (no mmap needed)
    │
    └─ YES → Is memory constrained?
        ├─ NO → Use Polars (fastest)
        │
        └─ YES → Use mmap (lowest memory)
            └─ Provide filename when registering source
```
