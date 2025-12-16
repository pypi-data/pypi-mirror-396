# Source Protocol - Simple Explanation

## The Core Idea

**Everything is an iterator. If your iterator function accepts optimization parameters, the engine uses them automatically.**

---

## Visual Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REGISTERS SOURCE                     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  engine.register("table", source_function)                  │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│         ENGINE CHECKS FUNCTION SIGNATURE                     │
│                                                               │
│  Does source_function accept:                                 │
│    - dynamic_where?                                           │
│    - dynamic_columns?                                         │
└─────────────────────────────────────────────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    ┌───────────────┐         ┌───────────────┐
    │   YES - Has   │         │   NO - Simple │
    │   Protocol    │         │   Iterator    │
    └───────────────┘         └───────────────┘
            │                           │
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│ OPTIMIZATIONS APPLY   │   │ NO OPTIMIZATIONS      │
│                       │   │                       │
│ • Filter pushdown     │   │ • All rows fetched    │
│ • Column pruning      │   │ • Filter in Python    │
└───────────────────────┘   └───────────────────────┘
```

---

## Code Examples

### Example A: Simple Iterator (No Protocol)

```python
# User writes this
def file_source():
    with open("data.jsonl") as f:
        for line in f:
            yield json.loads(line)

# Register
engine.register("products", file_source)

# What engine does:
# 1. Calls file_source() → gets all rows
# 2. Filters/joins in Python
# 3. No optimizations
```

### Example B: Protocol Iterator (With Optimizations)

```python
# User writes this
def database_source(dynamic_where=None, dynamic_columns=None):
    # Build SQL with optimizations
    columns = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(columns)} FROM products"
    if where:
        query += f" WHERE {where}"
    
    # Execute and return iterator
    cursor = execute(query)
    for row in cursor:
        yield dict(row)

# Register (SAME WAY!)
engine.register("products", database_source)

# What engine does:
# 1. Detects function accepts dynamic_where and dynamic_columns
# 2. Calls database_source(dynamic_where="id > 100", dynamic_columns=["id", "name"])
# 3. Database does filtering and column selection
# 4. Only needed data transferred
```

---

## Key Points

### 1. **No Flags Needed**

❌ **Old way (with flag):**
```python
engine.register("table", source, is_database_source=True)  # Flag!
```

✅ **New way (protocol):**
```python
engine.register("table", source)  # No flag! Engine detects automatically
```

### 2. **Same Registration, Different Behavior**

Both sources registered the same way:
```python
engine.register("simple", simple_source)      # No protocol
engine.register("optimized", optimized_source)  # Has protocol
```

Engine automatically:
- Uses optimizations for `optimized_source` (detects protocol)
- Uses normal execution for `simple_source` (no protocol)

### 3. **You Control Optimization**

If you want optimizations, write your function to accept the parameters:

```python
def my_source(dynamic_where=None, dynamic_columns=None):
    # Your code here
    # If you use these params → optimizations apply
    # If you ignore them → still works, just no optimization
    ...
```

If you don't need optimizations, just write a simple function:

```python
def my_source():
    # Simple iterator
    # No optimizations, but that's fine!
    ...
```

---

## Real-World Examples

### PostgreSQL Source (With Protocol)

```python
def pg_products(dynamic_where=None, dynamic_columns=None):
    conn = psycopg2.connect(...)
    cursor = conn.cursor()
    
    # Use protocol parameters
    cols = dynamic_columns or ["*"]
    where = dynamic_where or ""
    
    query = f"SELECT {', '.join(cols)} FROM products"
    if where:
        query += f" WHERE {where}"
    
    cursor.execute(query)
    for row in cursor:
        yield dict(row)

engine.register("products", pg_products)  # Auto-detected!
```

### JSONL File Source (No Protocol)

```python
def jsonl_products():
    with open("products.jsonl") as f:
        for line in f:
            yield json.loads(line)

engine.register("products", jsonl_products)  # Works fine!
```

### REST API Source (With Protocol - If API Supports It)

```python
def api_products(dynamic_where=None, dynamic_columns=None):
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where  # API supports filtering
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)  # API supports field selection
    
    response = requests.get("https://api.com/products", params=params)
    for item in response.json():
        yield item

engine.register("products", api_products)  # Auto-detected!
```

---

## Benefits

✅ **Simple**: One way to register sources  
✅ **Automatic**: Engine detects capabilities  
✅ **Flexible**: Works with any data source  
✅ **Clean**: No database code in core library  
✅ **Extensible**: Easy to add new source types  

---

## Summary

**Protocol = Function signature pattern**

- If your function accepts `(dynamic_where, dynamic_columns)` → optimizations apply
- If not → works normally, no optimizations

**No flags, no special classes, just function signatures!**

