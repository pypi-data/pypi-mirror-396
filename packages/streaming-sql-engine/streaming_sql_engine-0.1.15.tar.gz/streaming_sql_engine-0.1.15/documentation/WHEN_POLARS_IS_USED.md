# When Polars is Used - Complete Guide

## Overview

Polars is used in **4 main places** in the streaming SQL engine:

1. **Mmap Index Building** (for file-based joins)
2. **Join Operations** (PolarsLookupJoinIterator)
3. **Filtering** (PolarsBatchFilterIterator) 
4. **Projection** (PolarsBatchProjectIterator)

---

## 1. Mmap Index Building (`mmap_index.py`)

**When:** When building a position-based index for file-based joins

**Location:** `MmapPositionIndex.__init__()` → `_build_index_polars()`

**What it does:**
- Scans JSONL file line by line
- Collects (key_value, file_position) pairs in batches of 500,000
- Uses Polars `group_by()` to group positions by key_value (SIMD-accelerated)
- **10-100x faster** than Python dict grouping

**When triggered:**
```python
# When you register a file source with filename parameter
register_file_source(engine, "mongo", "data.jsonl", filename="data.jsonl")
# AND the join uses mmap (not in-memory or Polars join)
```

**Debug message:**
```
Building mmap position index with Polars (fast grouping) for data.jsonl...
Indexed 1,000,000 rows...
Mmap index built (Polars): 5,000,000 rows, 100,000 unique keys
```

**Code location:** `mmap_index.py:62-134`

---

## 2. Join Operations (`operators_polars.py`)

**When:** For JOIN operations when:
- `use_polars=True` (default)
- Polars is installed
- Mmap join is NOT available (mmap takes priority for memory)
- Right table has > 10,000 rows (threshold check)

**Location:** `executor.py:_build_join_iterator()` → `PolarsLookupJoinIterator`

**What it does:**
- Loads entire right table into Polars DataFrame
- Builds lookup index using Polars `group_by()` (SIMD-accelerated)
- Processes left rows in batches
- Performs vectorized joins using Polars operations
- **10-50x faster** than Python dict-based joins

**When triggered:**
```python
# When joining tables and mmap is not available
SELECT * FROM spryker JOIN mongo ON ...
# → Uses PolarsLookupJoinIterator if conditions met
```

**Debug message:**
```
Using POLARS LOOKUP JOIN (fast, vectorized)...
```

**Code location:** `executor.py:353-377`, `operators_polars.py:14-582`

**Priority order:**
1. **Mmap join** (if filename provided) - Best for memory
2. **Polars join** (if available and large enough) - Best for speed
3. **Python join** (fallback) - Works always

---

## 3. Filtering (`operators_polars.py`)

**When:** For WHERE clause filtering when:
- `use_polars=True` (default)
- Polars is installed
- `PolarsBatchFilterIterator` is available

**Location:** `executor.py:230-241`

**What it does:**
- Collects rows into batches (10,000 rows)
- Converts batch to Polars DataFrame
- Applies WHERE clause using Polars expressions (SIMD-accelerated)
- **10-200x faster** than Python row-by-row filtering

**When triggered:**
```python
# When applying WHERE clause after joins
SELECT * FROM ... WHERE spryker.query = 'reference'
# → Uses PolarsBatchFilterIterator if available
```

**Debug message:**
```
[OPTIMIZATION] Using Polars vectorized filtering (SIMD)
```

**Code location:** `executor.py:230-241`, `operators_polars.py:585-650`

**Note:** Currently may fall back to Python if not fully implemented.

---

## 4. Projection (`operators_polars.py`)

**When:** For SELECT column projection when:
- `use_polars=True` (default)
- Polars is installed
- `PolarsBatchProjectIterator` is available

**Location:** `executor.py:249-258`

**What it does:**
- Collects rows into batches (10,000 rows)
- Converts batch to Polars DataFrame
- Selects only requested columns using Polars (SIMD-accelerated)
- **10-50x faster** than Python row-by-row projection

**When triggered:**
```python
# When applying SELECT projection
SELECT spryker.id, mongo.price FROM ...
# → Uses PolarsBatchProjectIterator if available
```

**Debug message:**
```
[OPTIMIZATION] Using Polars vectorized projection
```

**Code location:** `executor.py:249-258`, `operators_polars.py:653-720`

---

## Summary Table

| Operation | When Polars is Used | Speedup | Location |
|-----------|---------------------|---------|----------|
| **Mmap Index Building** | Building file index | 10-100x | `mmap_index.py:62` |
| **Join Operations** | Mmap not available, table > 10K rows | 10-50x | `operators_polars.py:14` |
| **Filtering** | WHERE clause after joins | 10-200x | `operators_polars.py:585` |
| **Projection** | SELECT column selection | 10-50x | `operators_polars.py:653` |

---

## How to Enable/Disable

### Enable (Default)
```python
engine = Engine(use_polars=True)  # Default
```

### Disable
```python
engine = Engine(use_polars=False)  # Use pure Python
```

### Check if Polars is Available
```python
try:
    import polars as pl
    print("Polars is available!")
except ImportError:
    print("Polars not installed. Install with: pip install polars")
```

---

## Installation

Polars is **optional** but recommended:

```bash
# Install with Polars support
pip install streaming-sql-engine[polars]

# Or install Polars separately
pip install polars>=0.19.0
```

---

## Performance Impact

**Without Polars:**
- Pure Python operations
- Slower but works everywhere
- Lower memory for small datasets

**With Polars:**
- SIMD-accelerated operations
- 10-200x faster for large datasets
- Higher memory usage (loads data into DataFrames)

---

## Debug Messages

When `debug=True`, you'll see:

```
[OPTIMIZATION] Using Polars vectorized filtering (SIMD)
[OPTIMIZATION] Using Polars vectorized projection
Using POLARS LOOKUP JOIN (fast, vectorized)...
Building mmap position index with Polars (fast grouping)...
```

These messages confirm Polars is being used!

