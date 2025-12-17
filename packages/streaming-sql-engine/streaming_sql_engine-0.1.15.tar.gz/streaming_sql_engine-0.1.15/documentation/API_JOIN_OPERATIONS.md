# What Operations Are Used When Joining with APIs?

## Quick Answer

**No, it's not just JOIN!** The engine uses a **full SQL pipeline**:

1. **SELECT** (projection) - Choose which columns to return
2. **FROM** (scan) - Read from source (database, API, file, etc.)
3. **JOIN** - Combine data from multiple sources
4. **WHERE** (filter) - Filter rows based on conditions

---

## Complete Execution Pipeline

When you run a query with API sources, here's what happens:

```
SQL Query
   ↓
[1. PARSER] → AST
   ↓
[2. PLANNER] → LogicalPlan
   ↓
[3. EXECUTOR] → Iterator Pipeline:
   ├─ [SCAN] Read from root source (database/API/file)
   ├─ [FILTER] Apply WHERE clause
   ├─ [JOIN] Join with API source (or other sources)
   ├─ [JOIN] Join with more sources (if multiple joins)
   └─ [PROJECT] Apply SELECT projection
   ↓
Results
```

---

## Example: Database + API Join

### Your Query:

```sql
SELECT 
    p.sku,
    p.name,
    ap.price as api_price
FROM products p
JOIN api_prices ap ON p.sku = ap.sku
WHERE p.is_active = 1
```

### What Operations Are Used:

#### 1. **FROM** (Scan Operation)
```python
# Reads from "products" table (database)
[SCAN] Scanning table: products
```
- Reads rows from database
- Prefixes columns with table alias (`p.sku`, `p.name`, etc.)

#### 2. **WHERE** (Filter Operation)
```python
# Filters rows where is_active = 1
[FILTER] Applying WHERE clause
```
- Evaluates `p.is_active = 1` for each row
- Only keeps matching rows
- **Applied BEFORE join** (reduces data volume)

#### 3. **JOIN** (Join Operation)
```python
# Joins with API source
[JOIN 1/1] INNER JOIN api_prices
  → Using LOOKUP JOIN (building index...)
```
- **Builds index** from API source (loads all API data into memory)
- For each database row, **looks up** matching API row
- Combines matching rows

#### 4. **SELECT** (Projection Operation)
```python
# Selects only requested columns
[PROJECT] Applying SELECT projection
```
- Extracts only `p.sku`, `p.name`, `ap.price`
- Renames `ap.price` to `api_price`
- Returns final result

---

## Detailed Breakdown

### Operation 1: **SCAN** (FROM clause)

**What it does:**
- Reads from source (database, API, file, etc.)
- Prefixes columns with table alias
- Yields rows one at a time

**For API sources:**
```python
def api_source():
    # Your API function
    response = requests.get("https://api.example.com/data")
    for item in response.json():
        yield {"sku": item["sku"], "price": item["price"]}

# Engine calls this function
iterator = ScanIterator(api_source, "api_prices", "ap")
```

**Output:** Rows like `{"ap.sku": "SKU-001", "ap.price": 99.99}`

---

### Operation 2: **FILTER** (WHERE clause)

**What it does:**
- Evaluates WHERE conditions
- Keeps only matching rows
- **Applied early** (before joins, reduces data)

**Supported WHERE operations:**
- Comparisons: `=`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean: `AND`, `OR`, `NOT`
- NULL checks: `IS NULL`, `IS NOT NULL`
- IN clauses: `column IN (value1, value2, ...)`

**Example:**
```sql
WHERE p.is_active = 1 AND p.price > 100
```
- Evaluates both conditions
- Only keeps rows where both are true

---

### Operation 3: **JOIN** (JOIN clause)

**What it does:**
- Combines rows from two sources
- Matches rows based on join key
- Supports **INNER JOIN** and **LEFT JOIN**

**Join Algorithms:**

1. **Lookup Join** (default):
   - Builds hash index from right source (API)
   - For each left row, looks up matches
   - **For APIs:** Loads all API data into memory first

2. **Merge Join** (if both sorted):
   - Both sources must be sorted by join key
   - Merges like two sorted lists
   - **For APIs:** Requires API to return sorted data

**Example:**
```sql
JOIN api_prices ap ON p.sku = ap.sku
```
- Builds index: `{SKU-001: [row1], SKU-002: [row2], ...}`
- For each product row, looks up matching API price
- Combines: `{p.sku: "SKU-001", p.name: "Product", ap.price: 99.99}`

---

### Operation 4: **PROJECT** (SELECT clause)

**What it does:**
- Selects only requested columns
- Applies aliases (`AS` clauses)
- Transforms column names

**Example:**
```sql
SELECT p.sku, p.name, ap.price as api_price
```
- Input row: `{p.sku: "SKU-001", p.name: "Product", ap.price: 99.99, ap.currency: "USD", ...}`
- Output row: `{sku: "SKU-001", name: "Product", api_price: 99.99}`

---

## Complete Example Flow

### Query:
```sql
SELECT 
    p.sku,
    p.name,
    ap.price as api_price
FROM products p
JOIN api_prices ap ON p.sku = ap.sku
WHERE p.is_active = 1 AND ap.price > 50
```

### Execution Steps:

```
Step 1: [SCAN] products
  → Reads: {"id": 1, "sku": "SKU-001", "name": "Product A", "is_active": 1}
  → Output: {"p.id": 1, "p.sku": "SKU-001", "p.name": "Product A", "p.is_active": 1}

Step 2: [FILTER] WHERE p.is_active = 1
  → Evaluates: 1 == 1 → True
  → Keeps row

Step 3: [JOIN] api_prices
  → Builds index from API: {"SKU-001": [{"ap.sku": "SKU-001", "ap.price": 99.99}]}
  → Looks up "SKU-001" → Found!
  → Combines: {"p.sku": "SKU-001", "p.name": "Product A", "ap.sku": "SKU-001", "ap.price": 99.99}

Step 4: [FILTER] WHERE ap.price > 50
  → Evaluates: 99.99 > 50 → True
  → Keeps row

Step 5: [PROJECT] SELECT p.sku, p.name, ap.price as api_price
  → Extracts: {"sku": "SKU-001", "name": "Product A", "api_price": 99.99}
  → Yields final result
```

---

## What's NOT Just JOIN

### You Can Use:

✅ **SELECT** - Choose columns
```sql
SELECT p.sku, ap.price
```

✅ **FROM** - Specify source
```sql
FROM products p
```

✅ **WHERE** - Filter rows
```sql
WHERE p.is_active = 1 AND ap.price > 100
```

✅ **JOIN** - Combine sources
```sql
JOIN api_prices ap ON p.sku = ap.sku
```

✅ **Multiple JOINs** - Join many sources
```sql
FROM products p
JOIN api_prices ap ON p.sku = ap.sku
JOIN api_customers ac ON p.customer_id = ac.id
```

✅ **LEFT JOIN** - Keep unmatched rows
```sql
LEFT JOIN api_prices ap ON p.sku = ap.sku
```

---

## What's NOT Supported

❌ **GROUP BY** - Aggregations
```sql
-- NOT supported
SELECT category, COUNT(*) 
FROM products 
GROUP BY category
```

❌ **ORDER BY** - Sorting
```sql
-- NOT supported
SELECT * FROM products ORDER BY price DESC
```

❌ **Aggregations** - COUNT, SUM, AVG, etc.
```sql
-- NOT supported
SELECT COUNT(*) FROM products
```

❌ **Subqueries** - Nested queries
```sql
-- NOT supported
SELECT * FROM (SELECT * FROM products) p
```

---

## Summary

**When joining with APIs, you're using:**

1. ✅ **SELECT** - Column selection and aliasing
2. ✅ **FROM** - Source specification (database, API, file)
3. ✅ **WHERE** - Row filtering (applied before/after joins)
4. ✅ **JOIN** - Combining data from multiple sources

**It's a full SQL pipeline, not just JOIN!**

The engine processes queries in this order:
```
SCAN → FILTER → JOIN → JOIN → ... → FILTER → PROJECT
```

This gives you the power of SQL queries across different data sources (databases, APIs, files, etc.).

