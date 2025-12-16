# What is `where_to_params` and Why Do You Have It?

## What is `where_to_params`?

**`where_to_params`** is a function that converts a **SQL WHERE clause** into **API query parameters**.

### The Problem

When you write:

```sql
WHERE customers.active = true AND customers.country = 'US'
```

The engine passes this as a **SQL string** to your source function:

```python
dynamic_where = "customers.active = true AND customers.country = 'US'"
```

But your API expects **query parameters**:

```
GET /customers?active=true&country=US
```

**`where_to_params` converts SQL → API params!**

---

## How It Works

### Step 1: Engine Passes SQL WHERE Clause

```python
# Engine calls your source function with:
dynamic_where = "customers.active = true AND customers.country = 'US'"
```

### Step 2: Converter Converts to API Params

```python
def where_to_params(where_clause: str) -> dict:
    # Convert SQL WHERE clause to API query parameters
    params = {}

    if "active = true" in where_clause:
        params['active'] = 'true'

    if "country = 'US'" in where_clause:
        params['country'] = 'US'

    return params

# Result:
# params = {'active': 'true', 'country': 'US'}
```

### Step 3: API Request Uses Params

```python
# API request:
GET /customers?active=true&country=US
```

---

## Why You Have It in the Example

Looking at your FastAPI server (`examples/fastapi_server.py`):

```python
@app.get("/customers")
def get_customers(
    active: str = Query(default=None),      # Expects: ?active=true
    country: str = Query(default=None),     # Expects: ?country=US
    fields: str = Query(default=None),      # Expects: ?fields=id,name
):
```

**The API expects:**

- `?active=true` (not `?active=true` from SQL `active = true`)
- `?country=US` (not `?country='US'` from SQL `country = 'US'`)

---

## Do You Actually Need It?

**Probably NOT!** The **default converter** should handle this automatically!

### Default Converter (Automatic!)

The `register_api_source()` helper has a default converter that:

1. **Parses SQL** using sqlglot
2. **Extracts conditions** automatically:
   - `customers.active = true` → `params['active'] = 'true'`
   - `customers.country = 'US'` → `params['country'] = 'US'`

**So you can remove the custom converter!**

---

## Test: Can You Remove It?

Try this:

```python
# Remove the custom converter
register_api_source(
    engine,
    "customers",
    API_BASE_URL,
    "customers"
    # No where_to_params - use default!
)
```

**The default converter should work!** It automatically:

- Parses `customers.active = true` → `params['active'] = 'true'`
- Parses `customers.country = 'US'` → `params['country'] = 'US'`

---

## When You DO Need Custom Converter

Only if your API uses a **special format**:

### Example 1: Nested Parameters

```python
# API expects: ?filter[active]=true
# Default: ?active=true (doesn't match!)

def custom_converter(where_clause: str) -> dict:
    params = {}
    if "active = true" in where_clause:
        params['filter[active]'] = 'true'  # Nested format!
    return params
```

### Example 2: Different Parameter Names

```python
# API expects: ?is_active=true
# Default: ?active=true (wrong name!)

def custom_converter(where_clause: str) -> dict:
    params = {}
    if "active = true" in where_clause:
        params['is_active'] = 'true'  # Different name!
    return params
```

---

## Summary

### What `where_to_params` Does

**Converts SQL WHERE clause → API query parameters**

```python
# Input (SQL):
"customers.active = true AND customers.country = 'US'"

# Output (API params):
{'active': 'true', 'country': 'US'}

# Used in API request:
GET /customers?active=true&country=US
```

### Why You Have It

**You probably DON'T need it!** The default converter should work.

**Try removing it:**

```python
# Before (with custom converter):
register_api_source(engine, "customers", API_BASE_URL, "customers",
                   where_to_params=api_where_to_params)

# After (using default):
register_api_source(engine, "customers", API_BASE_URL, "customers")
```

**The default converter handles standard REST APIs automatically!**

---

## Key Points

1. **`where_to_params`** = Function that converts SQL WHERE → API params
2. **Default converter** handles most cases automatically
3. **Custom converter** only needed for special API formats
4. **Your example** probably doesn't need it - try removing it!

