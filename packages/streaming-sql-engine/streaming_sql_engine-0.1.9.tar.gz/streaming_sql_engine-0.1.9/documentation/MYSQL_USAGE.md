# MySQL Usage Guide

The Streaming SQL Engine now supports both **PostgreSQL** and **MySQL** databases.

## Quick Start with MySQL

### 1. Install Dependencies

```bash
pip install pymysql DBUtils
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file:

```env
db_host=your-mysql-host.com
db_port=3306
db_user=your_username
db_password=your_password
db_name=your_database
```

**Note:** Port 3306 is the default MySQL port. The library will auto-detect MySQL when it sees port 3306.

### 3. Use in Your Code

#### Option 1: Auto-Detection (Recommended)

```python
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
from dotenv import load_dotenv

load_dotenv()

# Auto-detects MySQL based on port 3306
pool = create_pool_from_env()

engine = Engine()
engine.register("users", create_table_source(pool, "users"))

for row in engine.query("SELECT * FROM users"):
    print(row)
```

#### Option 2: Explicit MySQL Connection

```python
from streaming_sql_engine import Engine, create_mysql_pool_from_env, create_table_source
from dotenv import load_dotenv

load_dotenv()

# Explicitly create MySQL pool
pool = create_mysql_pool_from_env()

engine = Engine()
engine.register("users", create_table_source(pool, "users"))

for row in engine.query("SELECT * FROM users"):
    print(row)
```

## Complete Example

```python
from streaming_sql_engine import Engine, create_mysql_pool_from_env, create_table_source, stream_query
from dotenv import load_dotenv
import json

load_dotenv()

# Create MySQL connection pool
pool = create_mysql_pool_from_env()

try:
    engine = Engine()

    # Register tables
    engine.register(
        "spy_product",
        create_table_source(pool, "spy_product", where_clause="is_active = 1")
    )

    engine.register(
        "spy_product_abstract",
        create_table_source(pool, "spy_product_abstract")
    )

    # Execute query with joins
    query = """
        SELECT sp.sku, spa.name AS product_name
        FROM spy_product sp
        JOIN spy_product_abstract spa ON sp.fk_product_abstract = spa.id_product_abstract
        WHERE sp.is_active = 1
    """

    # Process results
    with open('results.jsonl', 'w') as f:
        for row in engine.query(query):
            f.write(json.dumps(row) + '\n')
            print(row)

finally:
    pool.closeall()
```

## Custom Queries

For complex queries, use `stream_query` directly:

```python
from streaming_sql_engine import create_mysql_pool_from_env, stream_query

pool = create_mysql_pool_from_env()

def custom_source():
    query = """
        SELECT * FROM products
        WHERE category IN ('electronics', 'books')
        ORDER BY price DESC
    """
    return stream_query(pool, query)

engine.register("filtered_products", custom_source)
```

## Differences Between MySQL and PostgreSQL

| Feature         | MySQL              | PostgreSQL                        |
| --------------- | ------------------ | --------------------------------- |
| Default Port    | 3306               | 5432                              |
| Auto-Detection  | ✅ (by port)       | ✅ (by port)                      |
| Connection Pool | PooledDB (dbutils) | ThreadedConnectionPool (psycopg2) |
| Cursor Type     | DictCursor         | RealDictCursor                    |
| Parameter Style | `%s`               | `%s`                              |

## Troubleshooting

### Error: "pymysql and dbutils are required for MySQL support"

**Solution:** Install the required packages:

```bash
pip install pymysql DBUtils
```

### Error: "connection to server failed"

**Common causes:**

1. Wrong port (should be 3306 for MySQL)
2. Firewall blocking connection
3. Incorrect credentials
4. Database server not running

**Check:**

- Verify port in `.env` file is 3306
- Test connection with MySQL client: `mysql -h host -P 3306 -u user -p`

### Error: "SSL negotiation failed"

This usually means you're trying to use PostgreSQL driver (psycopg2) with a MySQL server.

**Solution:** Make sure you're using MySQL connector:

```python
# Correct
pool = create_mysql_pool_from_env()
# or
pool = create_pool_from_env()  # Will auto-detect if port is 3306
```

## Connection Pool Configuration

You can customize the connection pool:

```python
from streaming_sql_engine.db_connector import MySQLPool

pool = MySQLPool(
    host='localhost',
    port=3306,
    user='myuser',
    password='mypassword',
    database='mydb',
    maxconnections=200  # Maximum connections in pool
)
```

## Best Practices

1. **Always use connection pooling** - Don't create new connections for each query
2. **Close the pool when done** - Call `pool.closeall()` in a `finally` block
3. **Use environment variables** - Store credentials in `.env` file, not in code
4. **Handle exceptions** - Wrap database operations in try/except blocks
5. **Use streaming** - For large result sets, the engine streams rows automatically

## Next Steps

- See [QUICK_START.md](QUICK_START.md) for general usage
- Check [example_with_categories.py](example_with_categories.py) for a complete example
- Read [README.md](README.md) for full documentation
