# Why API Converter is Needed (And When You Can Skip It!)

## The Question

**Why do I need to write `api_where_to_params` if everything else is automatic?**

## The Answer

**You DON'T always need it!** The default converter handles most cases automatically. You only need a custom converter if your API uses a **special format**.

---

## How It Works

### Default Converter (Automatic!)

The `register_api_source()` helper has a **default converter** that automatically handles:

```python
# Just register - no converter needed!
register_api_source(engine, "customers", "http://localhost:8000", "customers")
```

**What the default converter does:**

1. **Parses SQL WHERE clause** using sqlglot
2. **Converts to API params** automatically:
   - `column = value` → `params[column] = value`
   - `active = true` → `params[active] = 'true'`
   - `price > 100` → `params[min_price] = '100'`
   - `price < 200` → `params[max_price] = '200'`
   - Multiple conditions (AND) → Multiple params

**Example:**

```sql
WHERE customers.active = true AND customers.price > 100
```

**Automatically converts to:**

```python
params = {
    'active': 'true',
    'min_price': '100'
}
```

---

## When You DON'T Need Custom Converter

### ✅ Standard REST APIs

If your API accepts standard query parameters:

```python
# API endpoint: GET /customers?active=true&min_price=100
# Default converter works perfectly!
register_api_source(engine, "customers", "http://api.com", "customers")
```

**No custom converter needed!**

---

## When You DO Need Custom Converter

### ❌ Special API Formats

If your API uses a **different format** than standard:

#### Example 1: Nested Parameters

```python
# API expects: ?filter[active]=true&filter[price][min]=100
# Default: ?active=true&min_price=100 (doesn't match!)

def custom_converter(where_clause: str) -> dict:
    params = {}
    # Convert to nested format
    if "active = true" in where_clause:
        params['filter[active]'] = 'true'
    if "price > 100" in where_clause:
        params['filter[price][min]'] = '100'
    return params

register_api_source(engine, "customers", "http://api.com", "customers",
                   where_to_params=custom_converter)
```

#### Example 2: Different Parameter Names

```python
# API expects: ?is_active=true&price_min=100
# Default: ?active=true&min_price=100 (wrong names!)

def custom_converter(where_clause: str) -> dict:
    params = {}
    if "active = true" in where_clause:
        params['is_active'] = 'true'  # Different name!
    if "price > 100" in where_clause:
        params['price_min'] = '100'  # Different name!
    return params

register_api_source(engine, "customers", "http://api.com", "customers",
                   where_to_params=custom_converter)
```

#### Example 3: JSON Body Instead of Query Params

```python
# API expects POST with JSON body: {"filter": {"active": true}}
# Default uses query params (doesn't match!)

def custom_converter(where_clause: str) -> dict:
    # This would need to modify the request method/body
    # More complex - might need custom source function instead
    ...
```

---

## Comparison: File Sources vs API Sources

### File Sources: Fully Automatic ✅

```python
# Files: Fully automatic - no converter needed!
register_file_source(engine, "products", "data/products.jsonl")
```

**Why?** Files use the same format (SQL WHERE clause) → same evaluation (Python evaluator)

### API Sources: Mostly Automatic ✅

```python
# APIs: Mostly automatic - converter only if API uses special format
register_api_source(engine, "customers", "http://api.com", "customers")
```

**Why?** APIs use different formats (query parameters) → need conversion (SQL → API params)

---

## Default Converter Capabilities

The default converter automatically handles:

### ✅ Equality Conditions

```sql
WHERE column = value
→ params[column] = value
```

### ✅ Boolean Conditions

```sql
WHERE active = true
→ params[active] = 'true'
```

### ✅ Comparison Conditions

```sql
WHERE price > 100
→ params[min_price] = '100'

WHERE price < 200
→ params[max_price] = '200'
```

### ✅ Multiple Conditions (AND)

```sql
WHERE active = true AND price > 100
→ params[active] = 'true', params[min_price] = '100'
```

### ❌ Complex Conditions

```sql
WHERE (active = true OR status = 'pending') AND price > 100
→ Not fully supported (needs custom converter)
```

---

## Summary

### When You DON'T Need Custom Converter

✅ **Standard REST APIs** with query parameters  
✅ **Simple WHERE clauses** (equality, comparisons)  
✅ **Standard parameter names** (column names match)

**Just use:**

```python
register_api_source(engine, "customers", "http://api.com", "customers")
```

### When You DO Need Custom Converter

❌ **Special API formats** (nested params, different names)  
❌ **Complex WHERE clauses** (OR, NOT, subqueries)  
❌ **Non-standard APIs** (GraphQL, custom formats)

**Provide custom converter:**

```python
def my_converter(where_clause: str) -> dict:
    # Custom conversion logic
    return params

register_api_source(engine, "customers", "http://api.com", "customers",
                   where_to_params=my_converter)
```

---

## Key Insight

**File sources:** Same format everywhere (SQL) → Fully automatic ✅  
**API sources:** Different formats (query params) → Mostly automatic, converter only if special format ⚠️

**The default converter handles 90% of cases!** You only need custom converter for special APIs.

