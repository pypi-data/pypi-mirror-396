# Quick Start Guide

Get up and running with the Streaming SQL Engine in 5 minutes.

## Step 1: Install the Library

```bash
# Navigate to the library directory
cd /path/to/sql_engine

# Install in editable mode (recommended)
pip install -e .
```

## Step 2: Set Up Database Connection (Optional)

Create a `.env` file in your project:

```env
db_host=localhost
db_port=5432
db_user=your_username
db_password=your_password
db_name=your_database
```

## Step 3: Use in Your Code

### Basic Example (In-Memory Data)

```python
from streaming_sql_engine import Engine

engine = Engine()

# Register data sources
def users_source():
    return iter([
        {"id": 1, "name": "Alice", "dept_id": 10},
        {"id": 2, "name": "Bob", "dept_id": 20},
    ])

def departments_source():
    return iter([
        {"id": 10, "name": "Engineering"},
        {"id": 20, "name": "Sales"},
    ])

engine.register("users", users_source)
engine.register("departments", departments_source)

# Execute query
query = """
    SELECT users.name, departments.name AS dept_name
    FROM users
    JOIN departments ON users.dept_id = departments.id
    WHERE users.id > 1
"""

for row in engine.query(query):
    print(row)
```

### PostgreSQL Example

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
from dotenv import load_dotenv

load_dotenv()

# Create connection pool
pool = create_pool_from_env()

# Create engine
engine = Engine()

# Register database tables
engine.register(
    "spy_product",
    create_table_source(pool, "spy_product", where_clause="is_active = 1")
)

engine.register(
    "spy_product_abstract",
    create_table_source(pool, "spy_product_abstract")
)

# Execute query
query = """
    SELECT sp.sku, spa.name AS product_name
    FROM spy_product sp
    JOIN spy_product_abstract spa ON sp.fk_product_abstract = spa.id_product_abstract
    WHERE sp.is_active = 1
"""

for row in engine.query(query):
    print(row)

# Clean up
pool.closeall()
```

## Common Use Cases

### 1. Filter and Join Multiple Tables

```python
engine.register("table1", create_table_source(pool, "table1"))
engine.register("table2", create_table_source(pool, "table2"))
engine.register("table3", create_table_source(pool, "table3"))

query = """
    SELECT t1.col1, t2.col2, t3.col3
    FROM table1 t1
    JOIN table2 t2 ON t1.id = t2.fk_id
    LEFT JOIN table3 t3 ON t1.id = t3.fk_id
    WHERE t1.status = 'active'
"""
```

### 2. Custom Source Function

```python
from streaming_sql_engine import stream_query

def custom_source():
    query = """
        SELECT * FROM products
        WHERE category IN ('electronics', 'books')
        ORDER BY price DESC
    """
    return stream_query(pool, query)

engine.register("filtered_products", custom_source)
```

### 3. Process Results to File

```python
import json

with open('results.jsonl', 'w') as f:
    for row in engine.query(query):
        f.write(json.dumps(row) + '\n')
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [INSTALLATION.md](INSTALLATION.md) for installation options
- See [example.py](example.py) and [example_with_categories.py](example_with_categories.py) for more examples
