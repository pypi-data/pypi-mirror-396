# Simple Source Functions: Why Less Code is Better

## The Question

**Why do source functions need so much code? Why can't they be simpler?**

## The Answer

**They CAN be simpler!** The engine handles filtering and column pruning automatically. Source functions should just **read and yield rows**.

---

## Simple Source (Recommended)

```python
def csv_source(filepath: str) -> Iterator[Dict]:
    """Simple source - engine handles everything."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Register
engine.register("products", lambda: csv_source("data.csv"))
```

**That's it!** Just 5 lines. The engine:

- ✅ Filters rows (using evaluator)
- ✅ Selects columns (column pruning)
- ✅ Applies WHERE clauses
- ✅ Handles joins

---

## Complex Source (Unnecessary)

```python
def csv_source(
    filepath: str,
    dynamic_where: Optional[str] = None,
    dynamic_columns: Optional[list] = None
) -> Iterator[Dict]:
    """Complex source - manual parsing."""
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)

        # Manual column pruning
        if dynamic_columns:
            columns_to_keep = [col for col in reader.fieldnames if col in dynamic_columns]
        else:
            columns_to_keep = reader.fieldnames

        for row in reader:
            # Manual filter parsing
            if dynamic_where:
                if "name = 'Electronics'" in dynamic_where:
                    if row.get('name') != 'Electronics':
                        continue

            # Manual column selection
            if dynamic_columns:
                row = {k: v for k, v in row.items() if k in columns_to_keep}

            yield row
```

**Why this is bad:**

- ❌ 30+ lines instead of 5
- ❌ Manual SQL parsing (error-prone)
- ❌ Duplicates engine logic
- ❌ Hard to maintain

---

## When to Use Protocol (Advanced)

**Use protocol ONLY when source can optimize better than engine:**

### ✅ Database Source (Use Protocol)

```python
def db_source(dynamic_where=None, dynamic_columns=None):
    """Database can filter/select efficiently."""
    query = "SELECT "
    query += ", ".join(dynamic_columns) if dynamic_columns else "*"
    query += " FROM table"
    if dynamic_where:
        query += f" WHERE {dynamic_where}"  # ✅ Database executes SQL
    return execute(query)
```

**Why:** Database can use indexes, SQL optimization, etc.

### ✅ API Source (Use Protocol)

```python
def api_source(dynamic_where=None, dynamic_columns=None):
    """API can filter/select via query parameters."""
    params = {}
    if dynamic_where:
        params['filter'] = dynamic_where  # ✅ API filters server-side
    if dynamic_columns:
        params['fields'] = ','.join(dynamic_columns)  # ✅ API selects server-side
    return requests.get(url, params=params)
```

**Why:** API can filter/select server-side (faster, less data transfer)

### ❌ File Source (Don't Use Protocol)

```python
def file_source(filepath: str) -> Iterator[Dict]:
    """File source - let engine handle it."""
    with open(filepath, 'r') as f:
        for row in read_file(f):
            yield row
```

**Why:** File sources can't optimize better than engine's evaluator. Manual parsing is slower and error-prone.

---

## Summary

**For file sources:**

- ✅ **Simple:** Just read and yield
- ✅ **Engine handles:** Filtering, column pruning, WHERE clauses
- ✅ **Less code:** 5 lines instead of 30+

**For database/API sources:**

- ✅ **Use protocol:** Can optimize better than engine
- ✅ **Pass SQL/parameters:** Let source handle filtering/selection

**Key insight:** The engine's evaluator is already optimized. Don't duplicate its logic in file sources!


