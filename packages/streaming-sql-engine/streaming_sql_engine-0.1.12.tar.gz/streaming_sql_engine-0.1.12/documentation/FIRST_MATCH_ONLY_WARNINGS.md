# `first_match_only=True` - Potential Issues and When to Use

## What It Does

When `first_match_only=True`, the join operator:

1. **Deduplicates the right side** during index building (keeps only first occurrence per key)
2. **Returns only first match** per left key (even if multiple matches exist)

This prevents cartesian products from duplicate keys, dramatically reducing output rows.

## Potential Problems

### 1. **Data Loss - Missing Valid Matches**

**Problem:** If you need ALL matches (one-to-many relationships), you'll only get one.

**Example:**

```python
# Spryker has 1 row with product_offer_reference='ABC'
# Mongo has 3 rows with product_offer_reference='ABC' (legitimate duplicates)

# With first_match_only=True:
# → Returns 1 row (only first mongo match)

# With first_match_only=False (standard SQL):
# → Returns 3 rows (all combinations)
```

**Impact:** You might miss important reconciliation issues if duplicates are legitimate.

### 2. **Non-Deterministic Results**

**Problem:** Which "first" match you get depends on file order, which may be inconsistent.

**Example:**

```python
# File order changes between runs:
# Run 1: mongo row A, then mongo row B (both have ref='ABC')
# → Returns row A

# Run 2: mongo row B, then mongo row A (same data, different order)
# → Returns row B
```

**Impact:** Results may differ between runs, making debugging difficult.

### 3. **Different from Standard SQL Behavior**

**Problem:** Standard SQL JOINs return ALL combinations. This breaks that expectation.

**Example:**

```sql
-- Standard SQL behavior:
-- If spryker has 1 row and mongo has 3 matching rows
-- → Returns 3 rows (all combinations)

-- With first_match_only=True:
-- → Returns 1 row (only first match)
```

**Impact:** Results don't match standard SQL expectations, which could confuse users.

### 4. **Business Logic Assumptions**

**Problem:** If your business logic expects to see all matches but only gets one, it might miss issues.

**Example:**

```python
# Business logic: "If mongo has multiple prices for same ref, flag as error"
# With first_match_only=True: Only sees first price, misses the error!
```

**Impact:** May hide data quality issues.

## When It's SAFE to Use

### ✅ **Your Reconciliation Use Case**

**Why it's safe:**

- Your original code uses dictionaries, which also deduplicate (keeps last value)
- Reconciliation logic expects one match per key
- You're matching records, not analyzing all combinations
- Performance is critical (millions of rows)

**Original code behavior:**

```python
def build_reference_dict(self, data):
    ref_dict = {}
    for line in data:
        ref_dict[line["product_offer_reference"]] = line  # Overwrites duplicates
    return ref_dict
```

**Note:** Original keeps LAST match, `first_match_only=True` keeps FIRST match. This is a minor difference, but both deduplicate.

### ✅ **When You Have One-to-One Relationships**

If join keys are unique (no duplicates), `first_match_only=True` has no effect.

### ✅ **When Performance is Critical**

If you have millions of rows and duplicates cause cartesian products, the speedup is worth it.

## When It's NOT SAFE to Use

### ❌ **When You Need All Matches**

If your business logic requires seeing ALL matches:

```python
# Don't use first_match_only=True if you need:
# - All price variations for same product
# - All status changes over time
# - Complete audit trail
```

### ❌ **When Results Must Be Deterministic**

If you need consistent results across runs:

```python
# Use first_match_only=False and ensure data is sorted
# Or use a deterministic deduplication strategy
```

### ❌ **When Doing Analytics**

If you're analyzing relationships and need all combinations:

```python
# Standard SQL behavior needed for:
# - Finding all possible combinations
# - Statistical analysis
# - Data exploration
```

## Recommendations for Your Reconciliation Script

### Current Setup (SAFE):

```python
self.engine = Engine(debug=False, use_polars=True, first_match_only=True)
```

**Why it's safe:**

1. ✅ Original code also deduplicates (dictionaries)
2. ✅ Reconciliation expects one match per key
3. ✅ Performance critical (millions of rows)
4. ✅ You're matching records, not analyzing combinations

### If You Need More Safety:

**Option 1: Add Warning for Duplicates**

```python
# In your processing, detect and warn about duplicates
if len(matches) > 1:
    print(f"WARNING: Found {len(matches)} matches for key {key}, using first only")
```

**Option 2: Make It Configurable**

```python
class PostProcessor:
    def __init__(self, first_match_only=True):
        self.engine = Engine(
            debug=False,
            use_polars=True,
            first_match_only=first_match_only
        )
```

**Option 3: Use Deterministic Deduplication**

```python
# Sort data before joining to ensure consistent "first" match
# Or use a specific field to determine which match to keep
```

## Summary

| Scenario                         | Use `first_match_only=True`? | Reason                                          |
| -------------------------------- | ---------------------------- | ----------------------------------------------- |
| **Reconciliation (your case)**   | ✅ **YES**                   | Matches original behavior, performance critical |
| **One-to-one relationships**     | ✅ **YES**                   | No effect, safe                                 |
| **Need all matches**             | ❌ **NO**                    | Will lose data                                  |
| **Analytics/exploration**        | ❌ **NO**                    | Need all combinations                           |
| **Deterministic results needed** | ⚠️ **MAYBE**                 | Depends on data ordering                        |

## Bottom Line

For your reconciliation script, `first_match_only=True` is **SAFE and RECOMMENDED** because:

1. It matches your original code's deduplication behavior
2. It dramatically improves performance (prevents cartesian products)
3. Your business logic expects one match per key

The only difference is that original code keeps LAST match, while `first_match_only=True` keeps FIRST match. If this matters, you can sort your data first to ensure consistent results.
