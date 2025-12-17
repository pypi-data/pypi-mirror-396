# Where Polars is Used in the Engine

## Summary

Polars is used in **3 main places** in the execution pipeline:

1. **JOIN Operations** (`PolarsLookupJoinIterator`) - Line 397-424 in `executor.py`
2. **FILTER Operations** (`PolarsBatchFilterIterator`) - Line 233-243 in `executor.py`
3. **PROJECT Operations** (`PolarsBatchProjectIterator`) - Line 252-262 in `executor.py`

---

## 1. JOIN Operations

**Location:** `executor.py:_build_join_iterator()` → Lines 397-424

**When Polars is used:**
- `use_polars=True` (default)
- `POLARS_AVAILABLE=True` (Polars installed)
- `should_use_polars(right_source)` returns `True` (right side ≥10K rows)
- Mmap join is NOT available (mmap takes priority when `filename` provided and `use_polars=False`)

**Code:**
```python
if (use_polars and POLARS_AVAILABLE and 
    should_use_polars(right_source, threshold=10000)):
    return PolarsLookupJoinIterator(...)
```

**What it does:**
- Loads entire right table into Polars DataFrame
- Builds lookup index using Polars `group_by()` (SIMD-accelerated)
- Processes left rows and performs vectorized joins
- **10-50x faster** than Python dict-based joins

**Debug message when used:**
```
[POLARS] ✓ Using POLARS LOOKUP JOIN (SIMD-accelerated)
[POLARS]   Columns: 6
[POLARS]   ⚡ First-match-only mode enabled
```

**Debug message when NOT used:**
```
[POLARS] Checking if Polars should be used...
[POLARS] Right side too small or estimation failed, using Python join instead
```

---

## 2. FILTER Operations

**Location:** `executor.py:execute_plan()` → Lines 233-243

**When Polars is used:**
- `use_polars=True` (default)
- `POLARS_AVAILABLE=True` (Polars installed)
- `PolarsBatchFilterIterator` is available
- WHERE clause exists (non-pushable conditions)

**Code:**
```python
if (use_polars and POLARS_AVAILABLE and PolarsBatchFilterIterator is not None):
    iterator = PolarsBatchFilterIterator(iterator, plan.where_expr, batch_size=10000, debug=debug)
```

**What it does:**
- Collects rows into batches (10,000 rows)
- Converts batch to Polars DataFrame
- Applies vectorized filter using Polars expressions (SIMD-accelerated)
- **20-100x faster** than row-by-row Python filtering

**Debug message when used:**
```
[POLARS] Using Polars vectorized filtering (SIMD-accelerated)
```

**Debug message when NOT used:**
```
[POLARS] Polars translation not available, using Python filtering
```

**Implementation:** `operators_polars.py:PolarsBatchFilterIterator` (Lines 335-428)

---

## 3. PROJECT Operations

**Location:** `executor.py:execute_plan()` → Lines 252-262

**When Polars is used:**
- `use_polars=True` (default)
- `POLARS_AVAILABLE=True` (Polars installed)
- `PolarsBatchProjectIterator` is available
- SELECT projection exists

**Code:**
```python
if (use_polars and POLARS_AVAILABLE and PolarsBatchProjectIterator is not None):
    iterator = PolarsBatchProjectIterator(iterator, plan.projections, batch_size=10000, debug=debug)
```

**What it does:**
- Collects rows into batches (10,000 rows)
- Converts batch to Polars DataFrame
- Applies SELECT projection using Polars column operations (SIMD-accelerated)
- **10-50x faster** than row-by-row Python projection

**Debug message when used:**
```
[POLARS] Using Polars vectorized projection (SIMD-accelerated)
```

**Debug message when NOT used:**
```
(No message - silently uses Python ProjectIterator)
```

**Implementation:** `operators_polars.py:PolarsBatchProjectIterator` (Lines 449-610)

---

## 4. Mmap Index Building (Indirect)

**Location:** `mmap_index.py:_build_index_polars()` → Lines 62-134

**When Polars is used:**
- Building mmap position index for file-based joins
- Used internally by `MmapLookupJoinIterator`
- Groups file positions by key using Polars `group_by()` (SIMD-accelerated)

**What it does:**
- Scans JSONL file line by line
- Collects (key_value, file_position) pairs in batches
- Uses Polars `group_by()` to group positions by key
- **10-100x faster** than Python dict grouping

**Note:** This is indirect usage - you don't control it directly, but it uses Polars internally.

---

## Execution Order

When you run a query, Polars is checked/used in this order:

```
1. [SCAN] Read from source (no Polars)
   ↓
2. [JOIN] Check if Polars should be used for join
   ├─ YES → Use PolarsLookupJoinIterator
   └─ NO → Use LookupJoinIterator (Python)
   ↓
3. [FILTER] Check if Polars should be used for WHERE
   ├─ YES → Use PolarsBatchFilterIterator
   └─ NO → Use FilterIterator (Python)
   ↓
4. [PROJECT] Check if Polars should be used for SELECT
   ├─ YES → Use PolarsBatchProjectIterator
   └─ NO → Use ProjectIterator (Python)
```

---

## Conditions for Polars Usage

### For JOIN:
✅ `use_polars=True`  
✅ `POLARS_AVAILABLE=True` (Polars installed)  
✅ `should_use_polars(right_source)` returns `True` (right side ≥10K rows)  
✅ Mmap join NOT available (or `use_polars=True` overrides mmap)

### For FILTER:
✅ `use_polars=True`  
✅ `POLARS_AVAILABLE=True` (Polars installed)  
✅ `PolarsBatchFilterIterator` available  
✅ WHERE clause exists  
✅ SQL expression can be translated to Polars expression

### For PROJECT:
✅ `use_polars=True`  
✅ `POLARS_AVAILABLE=True` (Polars installed)  
✅ `PolarsBatchProjectIterator` available  
✅ SELECT projection exists

---

## Why Polars Might NOT Be Used

### For JOIN:
❌ `use_polars=False`  
❌ Polars not installed (`POLARS_AVAILABLE=False`)  
❌ Right side too small (<10K rows)  
❌ `should_use_polars()` throws exception  
❌ Mmap join takes priority (when `filename` provided and `use_polars=False`)

### For FILTER:
❌ `use_polars=False`  
❌ Polars not installed  
❌ SQL expression can't be translated to Polars  
❌ `PolarsBatchFilterIterator` fails (falls back to Python)

### For PROJECT:
❌ `use_polars=False`  
❌ Polars not installed  
❌ `PolarsBatchProjectIterator` fails (falls back to Python)

---

## Your Current Case

**From your logs:**
```
Using LOOKUP JOIN (Python) (building index, columns: 6)...
```

**Why Polars is NOT being used:**
- The debug message `[POLARS] Checking if Polars should be used...` is missing
- This suggests `should_use_polars()` is failing silently
- Or the check isn't being reached

**Possible reasons:**
1. `should_use_polars()` throws exception (consumes iterator, then fails)
2. Right source function can't be called multiple times
3. Exception in `should_use_polars()` is silently caught

**To fix:**
- Check if Polars is installed: `pip show polars`
- Check debug output for `[POLARS]` messages
- The improved debug output should now show why Polars isn't being used

---

## Files Where Polars is Used

1. **`executor.py`** - Main execution logic
   - Lines 14-26: Import Polars operators
   - Lines 233-243: Filter with Polars
   - Lines 252-262: Project with Polars
   - Lines 397-424: Join with Polars

2. **`operators_polars.py`** - Polars implementations
   - `PolarsLookupJoinIterator` - Join operations
   - `PolarsBatchFilterIterator` - Filter operations
   - `PolarsBatchProjectIterator` - Project operations
   - `should_use_polars()` - Decision function

3. **`mmap_index.py`** - Mmap index building (indirect)
   - Uses Polars for grouping file positions

4. **`engine.py`** - Engine initialization
   - Line 23: `use_polars=True` default parameter
   - Line 125: Passes `use_polars` to `execute_plan()`

---

## Summary Table

| Operation | Polars Class | Location | When Used |
|-----------|-------------|----------|-----------|
| **JOIN** | `PolarsLookupJoinIterator` | `executor.py:397-424` | `use_polars=True` + right side ≥10K rows |
| **FILTER** | `PolarsBatchFilterIterator` | `executor.py:233-243` | `use_polars=True` + expression translatable |
| **PROJECT** | `PolarsBatchProjectIterator` | `executor.py:252-262` | `use_polars=True` + available |
| **MMAP INDEX** | Polars `group_by()` | `mmap_index.py:62-134` | When building mmap index |

---

## Quick Check: Is Polars Being Used?

**Look for these debug messages:**

✅ **Polars IS being used:**
```
[POLARS] ✓ Using POLARS LOOKUP JOIN (SIMD-accelerated)
[POLARS] Using Polars vectorized filtering (SIMD-accelerated)
[POLARS] Using Polars vectorized projection (SIMD-accelerated)
```

❌ **Polars is NOT being used:**
```
Using LOOKUP JOIN (Python) (building index...)
[POLARS] Right side too small or estimation failed, using Python join instead
[POLARS] Polars not available (not installed), falling back to Python
```

