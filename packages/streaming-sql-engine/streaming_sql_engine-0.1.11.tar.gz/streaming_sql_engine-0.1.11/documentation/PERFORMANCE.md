# Performance Comparison: Streaming SQL Engine vs Database Joins

## Quick Answer

**Database joins are typically 10-100x faster** than this streaming SQL engine for most cases.

## Why Database Joins Are Faster

### Database Advantages:

1. **Query Optimization**: Databases have sophisticated query optimizers that:

   - Choose optimal join algorithms (hash join, nested loop, merge join)
   - Use indexes efficiently
   - Reorder joins for better performance
   - Push down filters early

2. **Data Locality**: Data stays in the database:

   - No network transfer overhead
   - Efficient memory access patterns
   - Optimized for disk I/O

3. **Native Performance**: Written in C/C++:
   - Much faster than Python
   - Optimized data structures
   - Efficient memory management

### Streaming Engine Limitations:

1. **Python Overhead**:

   - Python is slower than C/C++
   - Dictionary operations have overhead
   - GIL (Global Interpreter Lock) limits parallelism

2. **Network Overhead**:

   - Each row transferred over network
   - Connection overhead
   - No query optimization

3. **Memory Usage**:

   - Lookup joins load entire tables into Python memory
   - Dictionary lookups are slower than database indexes

4. **No Query Optimization**:
   - Joins executed in order specified
   - No cost-based optimization
   - No index usage

## Performance Benchmarks (Estimated)

| Operation                      | Database Join | Streaming Engine | Speed Difference  |
| ------------------------------ | ------------- | ---------------- | ----------------- |
| Simple 2-table join (1M rows)  | ~0.5 seconds  | ~5-10 seconds    | **10-20x slower** |
| Complex 5-table join (1M rows) | ~1-2 seconds  | ~30-60 seconds   | **20-30x slower** |
| Filtered join (WHERE clause)   | ~0.1 seconds  | ~2-5 seconds     | **20-50x slower** |

_Note: Actual performance depends on data size, network latency, and hardware._

## When to Use Database Joins (Recommended)

✅ **Use database joins when:**

- All tables are in the same database
- You need maximum performance
- You have large datasets
- You need complex queries (GROUP BY, aggregations, etc.)
- You want to leverage database indexes

**Example:**

```sql
-- Do this in the database (FAST)
SELECT sp.sku, spa.name
FROM spy_product sp
JOIN spy_product_abstract spa ON sp.fk_abs = spa.id
WHERE sp.is_active = 1;
```

## When to Use Streaming SQL Engine

✅ **Use streaming engine when:**

- **Different data sources**: Joining data from different databases, APIs, files
- **Memory constraints**: Can't load full tables into memory
- **Streaming requirements**: Need to process results row-by-row as they arrive
- **Python processing**: Need to apply Python logic between joins
- **Cross-system joins**: Joining database + CSV + API data

**Example:**

```python
# Use streaming engine when joining different sources
engine.register("db_table", create_table_source(pool, "table1"))
engine.register("csv_data", lambda: read_csv_file("data.csv"))
engine.register("api_data", lambda: fetch_from_api())

# Join across different sources
for row in engine.query("SELECT * FROM db_table JOIN csv_data ..."):
    process(row)
```

## Performance Optimization Tips

If you must use the streaming engine, optimize it:

### 1. Use Merge Joins When Possible

```python
# Register tables sorted by join key
engine.register(
    "table1",
    create_table_source(pool, "table1", order_by="id"),
    ordered_by="id"  # Enables merge join
)
```

### 2. Minimize Lookup Table Size

- Use WHERE clauses to filter before joining
- Join smaller tables first
- Use filtered sources

### 3. Push Filters to Database

```python
# Good: Filter at database level
engine.register(
    "products",
    create_table_source(pool, "products", where_clause="is_active = 1")
)

# Bad: Filter in Python
# This loads all rows, then filters
```

### 4. Use Streaming for Large Results

- Process results as they arrive
- Don't collect all results in memory
- Write to file/stream immediately

## Real-World Use Case

**Your current example (`example_with_categories.py`):**

This would be **much faster** if done in the database:

```sql
-- Database query (FAST - recommended)
SELECT
    sc.category_key,
    sca.name as category_name,
    sp.sku as product_sku,
    spo.sf_merchant_ean,
    spo.product_offer_reference,
    spo.merchant_sku,
    spo.merchant_reference,
    spo.metadata,
    spo.sf_buy_button
FROM spy_product_offer spo
JOIN spy_product sp ON spo.concrete_sku = sp.sku
JOIN spy_product_abstract spa ON sp.fk_product_abstract = spa.id_product_abstract
JOIN spy_product_category spc ON spa.id_product_abstract = spc.fk_product_abstract
JOIN spy_category sc ON spc.fk_category = sc.id_category AND sc.is_active = 1
LEFT JOIN spy_category_attribute sca ON sc.id_category = sca.fk_category
WHERE sc.category_key IN ('cat1', 'cat2', ...)
  AND spo.metadata IS NOT NULL;
```

**Why use streaming engine instead?**

- If you need to join with data from another source (different DB, API, file)
- If you need to process each row with Python logic
- If you have memory constraints

## Summary

| Aspect           | Database Joins   | Streaming Engine  |
| ---------------- | ---------------- | ----------------- |
| **Speed**        | ⚡ Very Fast     | 🐌 Slower         |
| **Use Case**     | Same database    | Different sources |
| **Memory**       | Database manages | Python manages    |
| **Optimization** | Automatic        | Manual            |
| **Best For**     | Performance      | Flexibility       |

## Recommendation

**For your use case:**

- If all tables are in the same MySQL database → **Use database joins directly**
- If you need to join with external data → **Use streaming engine**
- If you need maximum performance → **Use database joins**

The streaming engine is a **flexibility tool**, not a **performance tool**.
