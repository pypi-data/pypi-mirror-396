# Handling Multiple Matches Without Cartesian Products

## The Problem

You have **legitimate duplicates** (multiple matches) but don't want cartesian products:

**Example:**
- Spryker: 1 row with `product_offer_reference: "ABC"`
- Mongo: 3 rows with `product_offer_reference: "ABC"` (different prices/timestamps)
- **Problem:** Standard join returns 3 rows (cartesian product)
- **Problem:** `first_match_only=True` returns only 1 row (loses data)

**What you want:**
- See all duplicates (or aggregate them)
- But avoid cartesian products (1 left × 3 right = 3 output rows is OK, but not 1 left × 100 right = 100 rows)

## Solutions

### Solution 1: Aggregate Duplicates Before Joining (Recommended)

**Strategy:** Pre-process the right side to aggregate duplicates before joining.

**Example: Take latest/max/min value:**

```python
def mongo_source_aggregated():
    """Aggregate duplicates by taking latest price."""
    from collections import defaultdict
    
    # Group by product_offer_reference, keep latest (or max/min)
    grouped = defaultdict(list)
    
    for row in original_mongo_source():
        key = row.get('product_offer_reference')
        if key:
            grouped[key].append(row)
    
    # For each key, take the row with latest timestamp (or max price, etc.)
    for key, rows in grouped.items():
        # Option 1: Take latest by timestamp
        latest = max(rows, key=lambda r: r.get('timestamp', ''))
        yield latest
        
        # Option 2: Take max price
        # max_price = max(rows, key=lambda r: float(r.get('price', 0)))
        # yield max_price
        
        # Option 3: Take first (deterministic)
        # yield rows[0]

engine.register("mongo", mongo_source_aggregated)
engine = Engine(use_polars=True, first_match_only=True)  # Still use this for safety
```

**Benefits:**
- No cartesian products (duplicates aggregated before join)
- Deterministic (you control which duplicate to keep)
- Can use business logic (latest, max, min, etc.)

**Limitations:**
- Requires pre-processing
- Loses some duplicate information

### Solution 2: Post-Process Results to Detect Duplicates

**Strategy:** Join with `first_match_only=True`, then detect and handle duplicates separately.

```python
def process_with_duplicate_detection(self, duplicates: set):
    """Process matches and flag duplicates."""
    query = """
        SELECT 
            spryker.product_offer_reference,
            mongo.price,
            mongo.status
        FROM spryker
        JOIN mongo ON spryker.product_offer_reference = mongo.product_offer_reference
        WHERE spryker.query = 'reference'
    """
    
    # Track seen references to detect duplicates
    seen_refs = {}
    duplicate_refs = set()
    
    for row in self.engine.query(query):
        ref = row['product_offer_reference']
        
        if ref in seen_refs:
            # Found duplicate - flag it
            duplicate_refs.add(ref)
            # Log or handle duplicate
            print(f"⚠️  Duplicate found for {ref}: {seen_refs[ref]} vs {row}")
        else:
            seen_refs[ref] = row
        
        yield row
    
    # Report duplicates
    if duplicate_refs:
        print(f"⚠️  Found {len(duplicate_refs)} references with duplicates in mongo")
```

**Benefits:**
- No cartesian products (only first match returned)
- Can detect and report duplicates
- Can handle duplicates separately

**Limitations:**
- Only sees first match (others are detected but not processed)
- Requires additional logic

### Solution 3: Use Deterministic Deduplication Strategy

**Strategy:** Deduplicate using a deterministic rule (e.g., sort by timestamp, then take first).

```python
def mongo_source_deterministic():
    """Deduplicate using deterministic sorting."""
    rows = list(original_mongo_source())
    
    # Sort by product_offer_reference, then by timestamp (descending)
    rows.sort(key=lambda r: (
        r.get('product_offer_reference', ''),
        r.get('timestamp', '')  # or price, or other field
    ), reverse=True)
    
    # Group and take first (which is latest due to reverse=True)
    seen = set()
    for row in rows:
        key = row.get('product_offer_reference')
        if key and key not in seen:
            seen.add(key)
            yield row

engine.register("mongo", mongo_source_deterministic)
engine = Engine(use_polars=True, first_match_only=True)
```

**Benefits:**
- Deterministic (same results every run)
- No cartesian products
- Can choose which duplicate to keep (latest, max, min, etc.)

**Limitations:**
- Requires sorting (memory/time overhead)
- Still loses duplicate information

### Solution 4: Aggregate in SQL (If Engine Supported)

**Strategy:** Use GROUP BY to aggregate duplicates (currently not supported, but planned).

**Future implementation:**
```sql
SELECT 
    spryker.product_offer_reference,
    MAX(mongo.price) as max_price,
    MIN(mongo.price) as min_price,
    COUNT(*) as duplicate_count
FROM spryker
JOIN mongo ON spryker.product_offer_reference = mongo.product_offer_reference
GROUP BY spryker.product_offer_reference
```

**Benefits:**
- Standard SQL approach
- No cartesian products
- Can aggregate (MAX, MIN, AVG, COUNT, etc.)

**Limitations:**
- Not currently supported in engine
- Would require GROUP BY implementation

### Solution 5: Two-Pass Approach

**Strategy:** First pass to detect duplicates, second pass to handle them.

```python
def process_with_two_passes(self):
    """Two-pass approach: detect then handle."""
    
    # Pass 1: Detect duplicates
    ref_counts = {}
    for row in mongo_source():
        ref = row.get('product_offer_reference')
        ref_counts[ref] = ref_counts.get(ref, 0) + 1
    
    duplicates = {ref: count for ref, count in ref_counts.items() if count > 1}
    
    # Pass 2: Handle duplicates
    if duplicates:
        # Option A: Use aggregated source
        mongo_agg = aggregate_mongo_source(duplicates)
        engine.register("mongo", mongo_agg)
    else:
        # Option B: Use original source
        engine.register("mongo", mongo_source)
    
    # Now join (no cartesian products)
    engine = Engine(use_polars=True, first_match_only=True)
    # ... rest of query
```

**Benefits:**
- Can detect duplicates first
- Can choose different strategies for duplicates vs non-duplicates
- Flexible

**Limitations:**
- Requires two passes (slower)
- More complex logic

## Recommended Approach for Your Use Case

### For Reconciliation Script:

**Option A: Aggregate by Latest/Max (Recommended)**

```python
def create_aggregated_mongo_source(mongo_filename):
    """Aggregate mongo duplicates by taking latest or max price."""
    from collections import defaultdict
    
    grouped = defaultdict(list)
    
    # Load and group
    with open(mongo_filename, 'r') as f:
        for line in f:
            row = json.loads(line)
            ref = row.get('product_offer_reference')
            if ref:
                grouped[ref].append(row)
    
    # For each group, take latest (or max price, or first)
    for ref, rows in grouped.items():
        # Option 1: Take latest by timestamp
        if any('timestamp' in r for r in rows):
            yield max(rows, key=lambda r: r.get('timestamp', ''))
        # Option 2: Take max price
        elif any('price' in r for r in rows):
            yield max(rows, key=lambda r: float(r.get('price', 0)))
        # Option 3: Take first (deterministic)
        else:
            yield rows[0]

# Register aggregated source
mongo_agg = create_aggregated_mongo_source('mongo_data.jsonl')
engine.register("mongo", lambda: mongo_agg)
engine = Engine(use_polars=True, first_match_only=True)  # Safety net
```

**Option B: Detect and Report Duplicates**

```python
def process_with_duplicate_reporting(self):
    """Join and report duplicates without cartesian products."""
    # Use first_match_only to prevent cartesian products
    engine = Engine(use_polars=True, first_match_only=True)
    
    # Join
    for row in engine.query(query):
        yield row
    
    # After join, check for duplicates in original data
    # (separate analysis)
    duplicate_refs = find_duplicates_in_mongo('mongo_data.jsonl')
    if duplicate_refs:
        print(f"⚠️  Warning: {len(duplicate_refs)} references have duplicates in mongo")
        # Log or handle separately
```

## Summary

**If you have legitimate duplicates but don't want cartesian products:**

1. ✅ **Aggregate before joining** (take latest/max/min) - Best for reconciliation
2. ✅ **Detect duplicates post-join** - Good for reporting
3. ✅ **Use deterministic deduplication** - Good for consistency
4. ✅ **Two-pass approach** - Good for complex logic

**Your current setup:**
```python
engine = Engine(use_polars=True, first_match_only=True)
```

**This is fine IF:**
- You only need one match per key (like your original dict-based approach)
- Duplicates are data quality issues (not legitimate)

**If you need to handle legitimate duplicates:**
- Use Solution 1 (aggregate before joining)
- Or Solution 2 (detect and report)

## Example: Your Reconciliation Case

**Your original code:**
```python
def build_reference_dict(self, data):
    ref_dict = {}
    for line in data:
        ref_dict[line["product_offer_reference"]] = line  # Keeps LAST match
    return ref_dict
```

**Equivalent in SQL engine:**
```python
# Option 1: Aggregate to keep latest (like original)
def mongo_source_latest():
    grouped = defaultdict(list)
    for row in original_mongo_source():
        grouped[row['product_offer_reference']].append(row)
    # Take last (like original dict behavior)
    for ref, rows in grouped.items():
        yield rows[-1]  # Last match (like dict overwrite)

engine.register("mongo", mongo_source_latest)
engine = Engine(use_polars=True, first_match_only=True)
```

This gives you the same behavior as your original code (keeps last match) without cartesian products!

