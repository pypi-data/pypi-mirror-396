# What Causes Cartesian Products in the Engine

## Overview

Cartesian products occur when **multiple rows match the same join key**, creating all possible combinations. This multiplies the output rows dramatically.

## Root Causes

### 1. **Duplicate Keys on Right Side** (Most Common)

**What happens:**
- Right side has multiple rows with the same join key value
- Each left row matches ALL right rows with that key
- Result: `left_rows × right_rows_with_same_key`

**Example with your data:**
```json
// Spryker (left) - 1 row
{"product_offer_reference": "MER304--.--8848--.--SF-14041057"}

// Mongo (right) - 3 rows with same merchant_reference
{"merchant_reference": "MER304", "price": "8.50"}
{"merchant_reference": "MER304", "price": "9.00"}  // duplicate!
{"merchant_reference": "MER304", "price": "10.00"}  // duplicate!
```

**If joining on `merchant_reference`:**
- 1 left row × 3 right rows = **3 output rows** (cartesian product)

**Code location:** `operators.py:220-232`
```python
if key_value not in self.lookup_index:
    self.lookup_index[key_value] = []
    self.lookup_index[key_value].append(prefixed_row)
else:
    # Key already exists - ADD to list (not overwrite)
    if deduplicate:
        # Skip duplicates - only keep first match
        duplicate_count += 1
    else:
        # Keep all matches (normal SQL behavior) ← CARTESIAN PRODUCT HERE
        self.lookup_index[key_value].append(prefixed_row)
```

### 2. **Duplicate Keys on Left Side**

**What happens:**
- Left side has multiple rows with the same join key value
- Each left row matches the same right rows
- Result: `left_rows_with_same_key × right_rows`

**Example:**
```json
// Spryker (left) - 2 rows with same reference
{"product_offer_reference": "MER304--.--8848--.--SF-14041057"}
{"product_offer_reference": "MER304--.--8848--.--SF-14041057"}  // duplicate!

// Mongo (right) - 1 row
{"merchant_reference": "MER304"}
```

**If joining on matching keys:**
- 2 left rows × 1 right row = **2 output rows** (cartesian product)

**Code location:** `operators.py:273-280`
```python
matches = self.lookup_index.get(left_key_value, [])
self._right_matches = [m for m in matches if m is not None]

# If first_match_only mode, only take first match
if self.first_match_only and len(self._right_matches) > 1:
    self._right_matches = self._right_matches[:1]  # ← Prevents cartesian
```

### 3. **`first_match_only=False` (Default)**

**What happens:**
- Engine keeps ALL matches per key (standard SQL behavior)
- If duplicates exist, all combinations are returned

**Code location:** `operators.py:163, 185`
```python
def __init__(self, ..., first_match_only=False):  # ← Default is False
    ...
    self._build_index(deduplicate=first_match_only)  # ← Passes False
```

**With `first_match_only=False`:**
- Right side duplicates → All matches kept → Cartesian products
- Left side duplicates → Each left row gets all matches → Cartesian products

**With `first_match_only=True`:**
- Right side duplicates → Only first match kept → No cartesian products
- Left side duplicates → Each left row gets only first match → No cartesian products

### 4. **Merge Join with Unsorted Data**

**What happens:**
- Merge join assumes sorted data
- On unsorted data, it buffers all rows with same key
- Creates cartesian products when duplicates exist

**Code location:** `operators.py:422-438`
```python
def _fill_right_buffer(self, target_key):
    """Fill right buffer with all rows matching target_key."""
    self._right_buffer = []
    # Collect all right rows with matching key ← CARTESIAN PRODUCT HERE
    while right_key_value == target_key:
        self._right_buffer.append(self._right_row)
        if not self._advance_right():
            break
        right_key_value = self._get_key_value(self._right_row, self.right_key)
```

**Note:** Merge join does NOT support `first_match_only` - it always creates cartesian products with duplicates.

### 5. **Mmap Join with Duplicates**

**What happens:**
- Mmap join stores file positions for all rows with same key
- Returns all matches (no deduplication)
- Creates cartesian products

**Code location:** `operators_mmap.py`
- Mmap join does NOT support `first_match_only` - it always creates cartesian products with duplicates.

## Your Specific Case

### Data Analysis:

**Spryker data:**
```json
{
  "product_offer_reference": "MER304--.--8848--.--SF-14041057",
  "merchant_reference": "MER304"
}
```

**Mongo data:**
```json
{
  "merchant_reference": "MER304",
  "product_id": 34017149
}
```

### Potential Cartesian Product Scenarios:

**Scenario 1: Joining on `merchant_reference`**
- If Mongo has multiple rows with `merchant_reference: "MER304"`
- Each Spryker row matches ALL Mongo rows with that reference
- Result: `spryker_rows × mongo_rows_with_MER304`

**Scenario 2: Joining on `product_offer_reference`**
- If Spryker has multiple rows with same `product_offer_reference`
- Each Mongo row matches ALL Spryker rows with that reference
- Result: `mongo_rows × spryker_rows_with_same_reference`

**Scenario 3: Wrong Join Key**
- If joining on fields that don't match exactly
- Example: `spryker.product_offer_reference` vs `mongo.merchant_reference`
- These don't match → No matches, but if they did match partially, could create cartesian products

## How to Prevent Cartesian Products

### Solution 1: Use `first_match_only=True`

```python
engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**What it does:**
- Deduplicates right side during index building (keeps only first match per key)
- Returns only first match per left key
- Prevents cartesian products

**Limitations:**
- Only works with `LookupJoinIterator` (Python) and `PolarsLookupJoinIterator`
- Does NOT work with `MergeJoinIterator` or `MmapLookupJoinIterator`

### Solution 2: Ensure Unique Join Keys

**Before joining:**
- Deduplicate data sources
- Ensure join keys are unique
- Use `DISTINCT` or group by join key

### Solution 3: Use Polars (with `first_match_only=True`)

```python
engine = Engine(debug=True, use_polars=True, first_match_only=True)
```

**Why:**
- Polars supports `first_match_only` deduplication
- Faster than Python fallback
- Prevents cartesian products

### Solution 4: Avoid Merge Join

**Don't use:**
```python
engine = Engine(use_polars=False)  # ← Allows merge join
engine.register("table1", source1, ordered_by="key")  # ← Enables merge join
engine.register("table2", source2, ordered_by="key")  # ← Enables merge join
```

**Use instead:**
```python
engine = Engine(use_polars=True, first_match_only=True)  # ← Forces Polars/Python lookup
```

## Detection

### Debug Output Shows:

**When cartesian products occur:**
```
Index built: 1,000,000 rows, 500,000 unique keys  ← Many duplicates!
```

**When deduplication happens:**
```
⚠️  Deduplicated: 500,000 duplicate keys removed (kept first match only)
```

**When Polars deduplicates:**
```
[POLARS] ⚠️  Deduplicated: 500,000 duplicate keys removed (kept first match only)
```

### Check Your Data:

**Before joining, check for duplicates:**
```python
# Count unique vs total rows
unique_keys = len(set(row['join_key'] for row in data))
total_rows = len(data)
duplicates = total_rows - unique_keys

if duplicates > 0:
    print(f"⚠️  Warning: {duplicates} duplicate keys found - cartesian products possible!")
```

## Summary

**Cartesian products are caused by:**
1. ✅ **Duplicate keys on right side** + `first_match_only=False`
2. ✅ **Duplicate keys on left side** + `first_match_only=False`
3. ✅ **Merge join** (always creates cartesian products with duplicates)
4. ✅ **Mmap join** (always creates cartesian products with duplicates)

**Prevent by:**
1. ✅ Use `first_match_only=True` (with Python/Polars joins)
2. ✅ Ensure unique join keys in data
3. ✅ Use Polars with `first_match_only=True`
4. ✅ Avoid merge join when duplicates exist

**Your reconciliation script:**
```python
self.engine = Engine(debug=True, use_polars=True, first_match_only=True)
```
✅ This configuration prevents cartesian products!

