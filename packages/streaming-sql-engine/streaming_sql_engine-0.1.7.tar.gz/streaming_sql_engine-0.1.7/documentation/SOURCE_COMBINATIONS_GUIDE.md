# Source Combinations Guide: All Possible Iterator Combinations

## Overview

With the new protocol-based architecture, you can combine **ANY** source types in joins:
- Databases (PostgreSQL, MySQL, MongoDB)
- Files (JSONL, CSV, Parquet)
- APIs (REST, GraphQL)
- Custom sources

**All work together seamlessly!**

---

## Source Types

### 1. Database Sources

#### PostgreSQL (With Protocol)
```python
def postgresql_source(dynamic_where=None, dynamic_columns=None):
    """PostgreSQL source with optimizations."""
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM products"
    if where:
        query += f" WHERE {where}"
    
    cursor.execute(query)
    for row in cursor:
        yield dict(row)
```

#### MySQL (With Protocol)
```python
def mysql_source(dynamic_where=None, dynamic_columns=None):
    """MySQL source with optimizations."""
    conn = pymysql.connect(...)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM orders"
    if where:
        query += f" WHERE {where}"
    
    cursor.execute(query)
    for row in cursor:
        yield dict(row)
```

#### MongoDB (With Protocol)
```python
def mongo_source(dynamic_where=None, dynamic_columns=None):
    """MongoDB source with optimizations."""
    collection = mongo_client.db.products
    
    filter_dict = {}
    if dynamic_where:
        # Convert SQL WHERE to MongoDB filter
        filter_dict = parse_sql_to_mongo(dynamic_where)
    
    projection = None
    if dynamic_columns:
        projection = {col: 1 for col in dynamic_columns}
    
    for doc in collection.find(filter_dict, projection):
        yield doc
```

---

### 2. File Sources

#### JSONL File (Simple - No Protocol)
```python
def jsonl_source():
    """Simple JSONL file source."""
    with open("products.jsonl") as f:
        for line in f:
            yield json.loads(line)
```

#### JSONL File (With Protocol - If You Can Filter)
```python
def jsonl_source_filtered(dynamic_where=None, dynamic_columns=None):
    """JSONL source with filtering capability."""
    with open("products.jsonl") as f:
        for line in f:
            row = json.loads(line)
            
            # Apply filter if provided
            if dynamic_where:
                if not matches_filter(row, dynamic_where):
                    continue
            
            # Select columns if provided
            if dynamic_columns:
                row = {k: v for k, v in row.items() if k in dynamic_columns}
            
            yield row
```

#### Parquet File (With Protocol)
```python
def parquet_source(dynamic_where=None, dynamic_columns=None):
    """Parquet file with column selection and filtering."""
    import pyarrow.parquet as pq
    
    # Column pruning: Only read needed columns
    table = pq.read_table("products.parquet", columns=dynamic_columns)
    
    # Filter pushdown: Parquet supports predicate pushdown
    if dynamic_where:
        table = table.filter(convert_where_to_predicate(dynamic_where))
    
    for row in table.to_pylist():
        yield row
```

#### CSV File (Simple)
```python
def csv_source():
    """Simple CSV file source."""
    import csv
    with open("products.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row
```

---

### 3. API Sources

#### REST API (With Protocol)
```python
def rest_api_source(dynamic_where=None, dynamic_columns=None):
    """REST API source with query parameters."""
    params = {}
    
    # Filter pushdown: API supports filtering
    if dynamic_where:
        params['filter'] = convert_sql_to_api_filter(dynamic_where)
    
    # Column pruning: API supports field selection
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.example.com/products", params=params)
    for item in response.json()['data']:
        yield item
```

#### GraphQL API (With Protocol)
```python
def graphql_source(dynamic_where=None, dynamic_columns=None):
    """GraphQL API source with query building."""
    # Build GraphQL query
    fields = dynamic_columns or ["*"]
    filter_clause = f'filter: "{dynamic_where}"' if dynamic_where else ""
    
    query = f"""
    {{
        products({filter_clause}) {{
            {' '.join(fields)}
        }}
    }}
    """
    
    response = requests.post(
        "https://api.example.com/graphql",
        json={"query": query}
    )
    
    for item in response.json()['data']['products']:
        yield item
```

#### REST API (Simple - No Protocol)
```python
def simple_api_source():
    """Simple REST API source - fetches all data."""
    response = requests.get("https://api.example.com/products")
    for item in response.json()['data']:
        yield item
```

---

### 4. Custom Sources

#### In-Memory Data
```python
def memory_source():
    """In-memory data source."""
    data = [
        {"id": 1, "name": "Product A"},
        {"id": 2, "name": "Product B"},
    ]
    return iter(data)
```

#### Generator Source
```python
def generator_source():
    """Generator-based source."""
    for i in range(1000):
        yield {"id": i, "value": i * 2}
```

---

## Join Combinations

### Combination 1: Database + Database

```python
from streaming_sql_engine import Engine

engine = Engine()

# PostgreSQL products
def pg_products(dynamic_where=None, dynamic_columns=None):
    # PostgreSQL implementation
    ...

# MySQL orders
def mysql_orders(dynamic_where=None, dynamic_columns=None):
    # MySQL implementation
    ...

engine.register("products", pg_products)
engine.register("orders", mysql_orders)

# Join PostgreSQL with MySQL!
query = """
    SELECT products.name, orders.total
    FROM products
    JOIN orders ON products.id = orders.product_id
    WHERE products.price > 100
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to PostgreSQL (`products.price > 100`)
- ✅ Column pruning on both sources
- ✅ Cross-database join works!

---

### Combination 2: Database + JSONL File

```python
engine = Engine()

# PostgreSQL products
def pg_products(dynamic_where=None, dynamic_columns=None):
    # PostgreSQL implementation
    ...

# JSONL file images
def jsonl_images():
    with open("images.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", pg_products)
engine.register("images", jsonl_images, filename="images.jsonl")  # Enables mmap!

# Join database with file!
query = """
    SELECT products.name, images.url
    FROM products
    JOIN images ON products.id = images.product_id
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to PostgreSQL
- ✅ Column pruning on PostgreSQL
- ✅ Mmap join for images file (low memory)
- ✅ Cross-source join works!

---

### Combination 3: Database + REST API

```python
engine = Engine()

# PostgreSQL products
def pg_products(dynamic_where=None, dynamic_columns=None):
    # PostgreSQL implementation
    ...

# REST API reviews
def api_reviews(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.com/reviews", params=params)
    for item in response.json():
        yield item

engine.register("products", pg_products)
engine.register("reviews", api_reviews)

# Join database with API!
query = """
    SELECT products.name, reviews.rating
    FROM products
    JOIN reviews ON products.id = reviews.product_id
    WHERE products.price > 100
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to PostgreSQL (`products.price > 100`)
- ✅ Filter pushdown to API (if API supports it)
- ✅ Column pruning on both sources
- ✅ Cross-source join works!

---

### Combination 4: JSONL File + JSONL File

```python
engine = Engine()

def jsonl_products():
    with open("products.jsonl") as f:
        for line in f:
            yield json.loads(line)

def jsonl_images():
    with open("images.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", jsonl_products, filename="products.jsonl")
engine.register("images", jsonl_images, filename="images.jsonl")

# Join two files!
query = """
    SELECT products.name, images.url
    FROM products
    JOIN images ON products.id = images.product_id
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Mmap joins for both files (low memory)
- ✅ File-to-file join works!

---

### Combination 5: API + API

```python
engine = Engine()

# GitHub API issues
def github_issues(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.github.com/issues", params=params)
    for item in response.json():
        yield item

# Stripe API customers
def stripe_customers(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['expand'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.stripe.com/customers", params=params)
    for item in response.json()['data']:
        yield item

engine.register("issues", github_issues)
engine.register("customers", stripe_customers)

# Join two APIs!
query = """
    SELECT issues.title, customers.email
    FROM issues
    JOIN customers ON issues.user_id = customers.id
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to both APIs (if supported)
- ✅ Column pruning on both APIs
- ✅ API-to-API join works!

---

### Combination 6: Database + File + API (3-Way Join)

```python
engine = Engine()

# PostgreSQL products
def pg_products(dynamic_where=None, dynamic_columns=None):
    # PostgreSQL implementation
    ...

# JSONL file categories
def jsonl_categories():
    with open("categories.jsonl") as f:
        for line in f:
            yield json.loads(line)

# REST API reviews
def api_reviews(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.com/reviews", params=params)
    for item in response.json():
        yield item

engine.register("products", pg_products)
engine.register("categories", jsonl_categories, filename="categories.jsonl")
engine.register("reviews", api_reviews)

# Join database + file + API!
query = """
    SELECT products.name, categories.name AS cat_name, reviews.rating
    FROM products
    JOIN categories ON products.category_id = categories.id
    JOIN reviews ON products.id = reviews.product_id
    WHERE products.price > 100
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to PostgreSQL
- ✅ Filter pushdown to API
- ✅ Column pruning on all sources
- ✅ Mmap join for categories file
- ✅ 3-way cross-source join works!

---

### Combination 7: MongoDB + Parquet File

```python
engine = Engine()

# MongoDB users
def mongo_users(dynamic_where=None, dynamic_columns=None):
    collection = mongo_client.db.users
    
    filter_dict = {}
    if dynamic_where:
        filter_dict = parse_sql_to_mongo(dynamic_where)
    
    projection = None
    if dynamic_columns:
        projection = {col: 1 for col in dynamic_columns}
    
    for doc in collection.find(filter_dict, projection):
        yield doc

# Parquet file orders
def parquet_orders(dynamic_where=None, dynamic_columns=None):
    import pyarrow.parquet as pq
    
    table = pq.read_table("orders.parquet", columns=dynamic_columns)
    if dynamic_where:
        table = table.filter(convert_where_to_predicate(dynamic_where))
    
    for row in table.to_pylist():
        yield row

engine.register("users", mongo_users)
engine.register("orders", parquet_orders)

# Join MongoDB with Parquet!
query = """
    SELECT users.name, orders.total
    FROM users
    JOIN orders ON users.id = orders.user_id
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ Filter pushdown to MongoDB
- ✅ Filter pushdown to Parquet
- ✅ Column pruning on both
- ✅ NoSQL + file join works!

---

### Combination 8: Simple Sources (No Protocol)

```python
engine = Engine()

# Simple in-memory data
def memory_products():
    return iter([
        {"id": 1, "name": "Product A"},
        {"id": 2, "name": "Product B"},
    ])

# Simple JSONL file
def jsonl_images():
    with open("images.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", memory_products)
engine.register("images", jsonl_images)

# Join simple sources!
query = """
    SELECT products.name, images.url
    FROM products
    JOIN images ON products.id = images.product_id
"""

for row in engine.query(query):
    print(row)
```

**What happens:**
- ✅ No optimizations (sources don't support protocol)
- ✅ Still works! (filtering/joining in Python)
- ✅ Simple sources work fine

---

## Complete Example: E-Commerce Data Pipeline

```python
from streaming_sql_engine import Engine

engine = Engine(debug=True)

# 1. PostgreSQL: Products (with protocol)
def pg_products(dynamic_where=None, dynamic_columns=None):
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM products"
    if where:
        query += f" WHERE {where}"
    
    cursor.execute(query)
    for row in cursor:
        yield dict(row)

# 2. JSONL File: Images (with mmap)
def jsonl_images():
    with open("images.jsonl") as f:
        for line in f:
            yield json.loads(line)

# 3. REST API: Reviews (with protocol)
def api_reviews(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)
    
    response = requests.get("https://api.com/reviews", params=params)
    for item in response.json():
        yield item

# 4. MongoDB: Categories (with protocol)
def mongo_categories(dynamic_where=None, dynamic_columns=None):
    collection = mongo_client.db.categories
    
    filter_dict = {}
    if dynamic_where:
        filter_dict = parse_sql_to_mongo(dynamic_where)
    
    projection = None
    if dynamic_columns:
        projection = {col: 1 for col in dynamic_columns}
    
    for doc in collection.find(filter_dict, projection):
        yield doc

# Register all sources
engine.register("products", pg_products)
engine.register("images", jsonl_images, filename="images.jsonl")
engine.register("reviews", api_reviews)
engine.register("categories", mongo_categories)

# Complex query across all sources!
query = """
    SELECT 
        products.name,
        categories.name AS category,
        images.url,
        reviews.rating
    FROM products
    JOIN categories ON products.category_id = categories.id
    JOIN images ON products.id = images.product_id
    JOIN reviews ON products.id = reviews.product_id
    WHERE products.price > 100
      AND reviews.rating >= 4
"""

for row in engine.query(query):
    print(row)
    # Process enriched product data
```

**What happens:**
- ✅ Filter pushdown to PostgreSQL (`products.price > 100`)
- ✅ Filter pushdown to API (`reviews.rating >= 4`)
- ✅ Column pruning on all sources
- ✅ Mmap join for images file
- ✅ 4-way cross-source join: PostgreSQL + MongoDB + JSONL + REST API!

---

## Summary Table

| Source 1 | Source 2 | Source 3 | Works? | Optimizations |
|----------|----------|----------|--------|---------------|
| PostgreSQL | MySQL | - | ✅ | Filter pushdown, column pruning |
| PostgreSQL | JSONL | - | ✅ | Filter pushdown, mmap join |
| PostgreSQL | REST API | - | ✅ | Filter pushdown on both |
| JSONL | JSONL | - | ✅ | Mmap joins |
| REST API | REST API | - | ✅ | Filter pushdown on both |
| MongoDB | Parquet | - | ✅ | Filter pushdown on both |
| PostgreSQL | JSONL | REST API | ✅ | All optimizations |
| Simple | Simple | - | ✅ | No optimizations (still works) |

---

## Key Takeaways

### ✅ **Any Source Can Join With Any Source**

- Database + Database ✅
- Database + File ✅
- Database + API ✅
- File + File ✅
- API + API ✅
- Any combination ✅

### ✅ **Optimizations Apply Automatically**

- If source implements protocol → optimizations apply
- If source doesn't → still works (no optimizations)
- Engine detects automatically

### ✅ **Multiple Join Types Supported**

- 2-way joins ✅
- 3-way joins ✅
- 4+ way joins ✅
- Any number of joins ✅

### ✅ **Mixed Source Types**

- Protocol sources + simple sources ✅
- Database + file + API ✅
- Any combination ✅

---

## Best Practices

1. **Use protocol when possible**
   - Implement `dynamic_where` and `dynamic_columns`
   - Get automatic optimizations

2. **Provide filename for large files**
   - Enables mmap joins
   - Reduces memory usage

3. **Use `ordered_by` for sorted data**
   - Enables merge joins
   - Faster for sorted data

4. **Combine sources strategically**
   - Put filtered sources first (filter pushdown)
   - Put large files with filename (mmap)
   - Put sorted sources with ordered_by (merge join)

---

## Conclusion

**With the new architecture, you can combine ANY source types!**

- ✅ Databases (PostgreSQL, MySQL, MongoDB)
- ✅ Files (JSONL, Parquet, CSV)
- ✅ APIs (REST, GraphQL)
- ✅ Custom sources
- ✅ Any combination!

**All work together seamlessly with automatic optimizations!**

