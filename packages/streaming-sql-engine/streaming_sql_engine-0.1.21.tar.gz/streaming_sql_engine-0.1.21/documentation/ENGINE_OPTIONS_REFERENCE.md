# Streaming SQL Engine - Options and Join Selection Reference

## Engine Initialization Options

### `Engine(debug=False, use_polars=True, first_match_only=False)`

**`debug` (bool, default: False)**

- Enables verbose logging of execution stages
- Shows: SQL parsing, logical plan building, iterator selection, join progress
- Prints which iterator type is used (MERGE JOIN, MMAP LOOKUP JOIN, POLARS LOOKUP JOIN, LOOKUP JOIN (Python))
- Shows optimization messages (filter pushdown, column pruning)
- Displays row counts and progress indicators

```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**`use_polars` (bool, default: True)**

- Enables Polars acceleration for joins, filtering, and projection
- When True: Prioritizes Polars over mmap and merge join (unless explicitly overridden)
- When False: Uses Python-based iterators (fallback)
- Requires Polars installed (`pip install polars`)
- Automatically falls back to Python if Polars unavailable or fails

```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**`first_match_only` (bool, default: False)**

- Prevents cartesian products from duplicate keys in joins
- When True: Deduplicates right side during index building, returns only first match per left key
- When False: Returns all matches (standard SQL behavior, can create cartesian products)
- Applies to: LookupJoinIterator (Python), PolarsLookupJoinIterator
- Does NOT apply to: MergeJoinIterator, MmapLookupJoinIterator (they handle duplicates differently)

```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

---

## Source Registration Options

### `engine.register(table_name, source_fn, ordered_by=None, filename=None)`

**`table_name` (str, required)**

- Name used in SQL queries to reference this source

**`source_fn` (callable, required)**

- Function returning iterator of row dictionaries
- If accepts `dynamic_where` and/or `dynamic_columns`: Enables filter pushdown and column pruning automatically
- Protocol detection: Engine checks function signature to detect optimization support

**`ordered_by` (str, optional)**

- Column name if source is pre-sorted by this column
- Enables merge join when both sides have matching `ordered_by` metadata
- Must match the join column name exactly
- Example: If joining on `product_id`, set `ordered_by="product_id"`

```python
engine.register("products", products_source, ordered_by="product_id")
engine.register("categories", categories_source, ordered_by="category_id")
```

**`filename` (str, optional)**

- File path if source is file-based (JSONL, CSV, etc.)
- Enables mmap-based joins (90-99% memory reduction)
- Only used when `use_polars=False` (Polars takes priority when enabled)
- Stores file positions instead of full rows in memory

```python
engine.register("products", products_source, filename="products.jsonl")
```

---

## Join Selection Logic

### Priority Order (checked in sequence):

**1. MERGE JOIN**

- **Conditions (ALL must be true):**
  - `use_polars=False` (Polars explicitly disabled)
  - Left side has `ordered_by` metadata matching left join column
  - Right side has `ordered_by` metadata matching right join column
- **When used:** Both tables pre-sorted by join keys
- **Performance:** O(n+m), minimal memory
- **Limitation:** Requires sorted data, produces incorrect results on unsorted data
- **Note:** Merge join can create cartesian products if data has duplicates (not deduplicated)

```python
engine = Engine(debug=True, use_polars=False, first_match_only=False)
engine.register("left_table", left_source, ordered_by="join_key")
engine.register("right_table", right_source, ordered_by="join_key")
```

**2. MMAP LOOKUP JOIN**

- **Conditions (ALL must be true):**
  - `MMAP_AVAILABLE` (mmap module available)
  - `MmapLookupJoinIterator` available
  - `filename` provided in source metadata
  - `use_polars=False` (Polars explicitly disabled)
- **When used:** File-based sources with memory constraints
- **Performance:** Similar to in-memory joins, 90-99% memory reduction
- **Memory:** Stores file positions only, reads rows on-demand from disk
- **Fallback:** Falls back to Polars/Python if mmap fails

```python
engine = Engine(debug=True, use_polars=False, first_match_only=False)
engine.register("products", products_source, filename="products.jsonl")
```

**3. POLARS LOOKUP JOIN**

- **Conditions (ALL must be true):**
  - `use_polars=True` (explicitly enabled)
  - `POLARS_AVAILABLE` (Polars installed)
  - `should_use_polars()` returns True (right side has ≥10,000 rows estimated)
- **When used:** Large datasets, Polars enabled, no mmap/merge join conditions met
- **Performance:** 10-50x faster than Python (SIMD-accelerated)
- **Memory:** Loads full right side into Polars DataFrame
- **Features:** Supports `first_match_only` deduplication
- **Fallback:** Falls back to Python if Polars fails

```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**4. LOOKUP JOIN (Python)**

- **Conditions:** Fallback when none of above apply
- **When used:** Small datasets, Polars disabled/unavailable, no mmap/merge conditions
- **Performance:** Standard Python dict-based lookup
- **Memory:** Stores full row dictionaries in memory
- **Features:** Supports `first_match_only` deduplication

```python
engine = Engine(debug=True, use_polars=False, first_match_only=True)
engine.register("products", products_source)
```

---

## Optimization Features

### Column Pruning

- **What:** Only requests needed columns from sources
- **When:** Source function accepts `dynamic_columns` parameter
- **Benefit:** Reduces I/O and memory usage
- **Automatic:** Detected via function signature inspection

### Filter Pushdown

- **What:** Pushes WHERE clauses to data sources for early filtering
- **When:** Source function accepts `dynamic_where` parameter
- **Benefit:** Reduces rows processed upstream
- **Automatic:** Detected via function signature inspection
- **Limitation:** Only pushes filters referencing single table (root table or joined table)

### Polars Vectorization

- **What:** Uses SIMD instructions for batch processing
- **When:** `use_polars=True` and Polars available
- **Applied to:** Joins, filtering (FilterIterator), projection (ProjectIterator)
- **Benefit:** 10-50x speedup for large datasets

### Mmap Memory Efficiency

- **What:** Stores file positions instead of full rows
- **When:** `filename` provided and `use_polars=False`
- **Benefit:** 90-99% memory reduction for large files
- **Trade-off:** Slightly slower than in-memory (but still fast due to mmap)

---

## Join Type Behavior

### INNER JOIN

- Returns rows where join keys match on both sides
- If no match: Row skipped
- With duplicates: Creates cartesian product (unless `first_match_only=True`)

### LEFT JOIN

- Returns all rows from left side
- If match found: Combines left + right columns
- If no match: Right columns set to NULL
- With duplicates: Creates cartesian product (unless `first_match_only=True`)

---

## `first_match_only` Behavior

### When `first_match_only=True`:

**LookupJoinIterator (Python):**

- During `_build_index()`: Only keeps first row per key in lookup dict
- During `__next__()`: If multiple matches found, only returns first
- Result: Prevents cartesian products, faster execution

```python
engine = Engine(debug=True, use_polars=False, first_match_only=True)
```

**PolarsLookupJoinIterator:**

- During `_build_polars_index()`: Uses `group_by().first()` to deduplicate
- During `__next__()`: If multiple matches found, only returns first
- Result: Prevents cartesian products, faster execution

```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**MergeJoinIterator:**

- NOT supported (merge join handles duplicates via buffering mechanism)
- Warning: Merge join can still create cartesian products with duplicates

**MmapLookupJoinIterator:**

- NOT supported (mmap uses position-based index, deduplication not implemented)
- Warning: Mmap join can still create cartesian products with duplicates

---

## Decision Flow Summary

```
Is use_polars=True?
├─ YES → Skip merge join, skip mmap (unless filename explicitly provided)
│   └─ Use Polars if available and right side ≥10K rows
│       └─ Fallback to Python if Polars fails/unavailable
│
└─ NO → Check merge join conditions
    ├─ Both sides sorted? → Use MERGE JOIN
    └─ Not sorted → Check mmap conditions
        ├─ Filename provided? → Use MMAP LOOKUP JOIN
        └─ No filename → Use Python LOOKUP JOIN
```

---

## Key Takeaways

- **`use_polars=True`**: Prioritizes Polars, skips merge join and mmap (unless explicitly overridden)
- **`first_match_only=True`**: Prevents cartesian products in Python and Polars joins (not merge/mmap)
- **`ordered_by`**: Enables merge join (only when `use_polars=False`)
- **`filename`**: Enables mmap join (only when `use_polars=False`)
- **Merge join**: Requires sorted data, can create cartesian products with duplicates
- **Polars**: Fastest for unsorted data, supports `first_match_only`
- **Mmap**: Lowest memory, requires file-based sources, doesn't support `first_match_only`
