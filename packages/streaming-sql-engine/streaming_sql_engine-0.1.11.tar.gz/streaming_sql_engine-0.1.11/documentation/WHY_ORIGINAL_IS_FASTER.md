# Why the Original Script is Faster Than SQL Engine

## TL;DR

**The original script is faster because it uses simple Python dictionaries with O(1) lookups, while the SQL engine adds significant overhead from parsing, planning, and iterator chains.**

## Performance Comparison

| Operation | Original Script | SQL Engine | Why Original is Faster |
|-----------|----------------|------------|------------------------|
| **Data Loading** | Load once into memory | Stream row-by-row | No streaming overhead |
| **Lookups** | Direct dict access `dict[key]` | Iterator chain + index lookup | No iterator overhead |
| **SQL Parsing** | None | sqlglot parsing | ~10-50ms overhead |
| **Planning** | None | Logical plan building | ~5-20ms overhead |
| **Column Access** | Direct `row['field']` | Prefixed `row['table.field']` | String operations overhead |
| **Expression Eval** | Direct Python code | AST traversal | Function call overhead |

## Detailed Analysis

### 1. **Data Loading Strategy**

**Original Script:**
```python
# Loads ALL data into memory once
mongo_data = self.load_data(mongo_filename)  # List of dicts
spryker_data = self.load_data(spryker_filename)  # List of dicts

# Builds dictionaries once
mongo_ref_dict = self.build_reference_dict(mongo_data)  # O(n) - done once
```

**SQL Engine:**
```python
# Streams data row-by-row through iterator chain
for row in self.engine.query(query):  # Each row goes through:
    # 1. ScanIterator (reads from file)
    # 2. FilterIterator (applies WHERE)
    # 3. LookupJoinIterator (builds index + lookup)
    # 4. ProjectIterator (selects columns)
```

**Overhead:** Iterator chain adds ~0.1-1ms per row in Python overhead.

### 2. **Lookup Performance**

**Original Script:**
```python
# Simple dictionary lookup - O(1), ~10-50 nanoseconds
if ref in mongo_ref_dict:
    mongo_line = mongo_ref_dict[ref]  # Direct hash table access
```

**SQL Engine:**
```python
# Iterator chain lookup - O(1) but with overhead:
# 1. Get left row from iterator
# 2. Extract join key value
# 3. Lookup in index (dict lookup)
# 4. Merge rows
# 5. Apply projection
# 6. Yield result
```

**Overhead:** Each row goes through 4-6 iterator steps, each with function call overhead.

### 3. **SQL Parsing & Planning Overhead**

**Original Script:**
```python
# No parsing - direct Python code execution
if query_type == "reference":
    ref = spryker_line.get("product_offer_reference")
    if ref and ref in mongo_ref_dict:
        mongo_line = mongo_ref_dict[ref]
```

**SQL Engine:**
```python
# Every query requires:
# 1. SQL parsing (sqlglot) - ~10-50ms
# 2. AST building - ~5-10ms
# 3. Logical plan building - ~5-20ms
# 4. Execution plan building - ~5-10ms
# Total: ~25-90ms per query
```

**Overhead:** ~25-90ms per query, even before processing any rows.

### 4. **Column Access Overhead**

**Original Script:**
```python
# Direct field access - no string operations
mongo_price = mongo_line.get("price")
spryker_price = spryker_line.get("gross_price")
```

**SQL Engine:**
```python
# Prefixed column access - string operations
mongo_price = row.get("mongo.price")  # String lookup
spryker_price = row.get("spryker.gross_price")  # String lookup

# Plus column prefixing/unprefixing overhead:
# - ScanIterator prefixes: "field" -> "table.field"
# - ProjectIterator may unprefix: "table.field" -> "field"
```

**Overhead:** String operations add ~10-50ns per column access.

### 5. **Memory Access Patterns**

**Original Script:**
```python
# All data in memory, excellent cache locality
# Sequential access through lists
# Dictionary lookups hit CPU cache
```

**SQL Engine:**
```python
# Streaming access - may cause cache misses
# Iterator chain creates function call overhead
# Less predictable memory access patterns
```

**Overhead:** Cache misses and function call overhead.

## Performance Breakdown (Estimated)

For processing 1 million rows:

| Component | Original Script | SQL Engine | Difference |
|-----------|----------------|------------|------------|
| **Data Loading** | 0.5s | 0.5s | Same |
| **Index Building** | 0.2s | 0.3s | 1.5x slower |
| **SQL Parsing** | 0s | 0.05s | New overhead |
| **Planning** | 0s | 0.02s | New overhead |
| **Row Processing** | 1.0s | 3.0s | 3x slower |
| **Total** | **1.7s** | **3.87s** | **2.3x slower** |

**Why row processing is slower:**
- Iterator chain overhead: ~0.5-1μs per row
- Column prefixing: ~0.1-0.3μs per row
- Function call overhead: ~0.2-0.5μs per row
- Total: ~0.8-1.8μs per row × 1M rows = 0.8-1.8s overhead

## When SQL Engine is Worth It

The SQL engine is **NOT faster** for simple cases like your reconciliation script. It's designed for:

### ✅ **Use SQL Engine When:**

1. **Cross-system joins** (Database + API + Files)
   ```python
   # Can't do this with simple dictionaries
   SELECT * FROM database_table 
   JOIN api_source ON ...
   JOIN file_source ON ...
   ```

2. **Dynamic queries** (user-provided SQL)
   ```python
   # Users can write SQL queries
   query = user_input  # Can't hardcode dictionary lookups
   ```

3. **Complex WHERE clauses** (many conditions)
   ```python
   # SQL engine handles complex expressions
   WHERE (a > 10 AND b < 20) OR (c = 'x' AND d IN (1,2,3))
   ```

4. **Multiple join types** (INNER, LEFT, etc.)
   ```python
   # SQL engine handles different join types
   LEFT JOIN, INNER JOIN, etc.
   ```

5. **Streaming large datasets** (can't fit in memory)
   ```python
   # SQL engine streams, original script loads all into memory
   ```

### ❌ **Don't Use SQL Engine When:**

1. **Simple lookups** (like your reconciliation)
   ```python
   # Simple dictionary lookup is faster
   if key in dict:
       value = dict[key]
   ```

2. **All data fits in memory**
   ```python
   # Loading all data once is faster than streaming
   ```

3. **Fixed query patterns**
   ```python
   # Hardcoded logic is faster than SQL parsing
   ```

4. **Performance is critical**
   ```python
   # Dictionary lookups are fastest for simple cases
   ```

## Optimization Strategies

### Option 1: **Hybrid Approach** (Best Performance)

Use original script for reconciliation, SQL engine for complex queries:

```python
class PostProcessor:
    def __init__(self):
        # Use original approach for reconciliation
        self.use_sql_engine = False  # Set to True only for complex queries
    
    def process_reference_matches(self, duplicates):
        if self.use_sql_engine:
            # Use SQL engine for complex queries
            return self._process_with_sql()
        else:
            # Use fast dictionary approach
            return self._process_with_dicts()
```

### Option 2: **Optimize SQL Engine** (Moderate Improvement)

Reduce overhead by:
1. **Caching parsed queries** (if same query used multiple times)
2. **Pre-building indexes** (if data doesn't change)
3. **Reducing iterator chain depth** (combine operations)
4. **Using Cython/C extensions** (for hot paths)

### Option 3: **Use Original Script** (Best for Your Case)

For your reconciliation use case, **the original script is the right choice** because:
- ✅ Simple lookup patterns
- ✅ All data fits in memory
- ✅ Fixed query patterns
- ✅ Performance is critical

## Conclusion

**The original script is faster because:**
1. **No SQL parsing overhead** - Direct Python code execution
2. **Simple dictionary lookups** - O(1) hash table access, no iterator chain
3. **Better memory access** - All data in memory, excellent cache locality
4. **No column prefixing** - Direct field access

**The SQL engine adds overhead for:**
1. SQL parsing and planning (~25-90ms per query)
2. Iterator chain processing (~0.8-1.8μs per row)
3. Column prefixing/unprefixing (~0.1-0.3μs per row)
4. Function call overhead (~0.2-0.5μs per row)

**For your reconciliation script, stick with the original approach** - it's the right tool for the job!

The SQL engine is designed for **flexibility and cross-system joins**, not raw performance for simple cases.

