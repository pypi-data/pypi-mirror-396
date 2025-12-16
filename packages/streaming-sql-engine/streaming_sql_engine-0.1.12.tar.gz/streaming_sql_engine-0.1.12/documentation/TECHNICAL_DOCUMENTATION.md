# Technical Documentation: Streaming SQL Engine

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Query Processing Pipeline](#query-processing-pipeline)
4. [Execution Model](#execution-model)
5. [Join Algorithms](#join-algorithms)
6. [Expression Evaluation](#expression-evaluation)
7. [Data Flow](#data-flow)
8. [Design Decisions](#design-decisions)
9. [Code Structure](#code-structure)
10. [Performance Characteristics](#performance-characteristics)

---

## Architecture Overview

The Streaming SQL Engine is a **row-by-row SQL execution engine** that processes queries using Python iterators. Unlike traditional database engines that load entire tables, this engine streams data through a pipeline of operators.

### Core Principles

1. **Streaming**: Process one row at a time, never loading full tables
2. **Iterator-based**: Use Python's iterator protocol for lazy evaluation
3. **Pipeline Architecture**: Chain operators together to form execution pipelines
4. **Memory Efficient**: Only materialize lookup-side tables for joins

### High-Level Flow

```
SQL Query → Parser → Logical Plan → Executor → Iterator Pipeline → Results
```

---

## System Components

### 1. Engine (`engine.py`)

**Purpose**: Main public API for the library

**Responsibilities**:

- Register table sources
- Accept SQL queries
- Coordinate parsing, planning, and execution
- Return result generators

**Key Design**:

- Stores registered sources as callable functions
- Each source function returns an iterator of dictionaries
- Metadata tracking (e.g., `ordered_by` for merge joins)

**Code Logic**:

```python
class Engine:
    def __init__(self):
        self._sources = {}  # table_name -> source_function
        self._source_metadata = {}  # table_name -> metadata

    def register(self, table_name, source_fn, ordered_by=None):
        # Store source function and metadata
        # Source function must return Iterator[Dict[str, Any]]

    def query(self, sql: str):
        # 1. Parse SQL → AST
        # 2. Build logical plan from AST
        # 3. Execute plan → return generator
```

---

### 2. Parser (`parser.py`)

**Purpose**: Convert SQL string into Abstract Syntax Tree (AST)

**Technology**: Uses `sqlglot` library for SQL parsing

**Logic**:

1. Try multiple SQL dialects (MySQL, PostgreSQL, SQLite)
2. Parse SQL string into AST
3. Validate that only SELECT queries are supported
4. Check for unsupported constructs (GROUP BY, ORDER BY, etc.)

**Key Implementation Details**:

- **Dialect Auto-Detection**: Tries MySQL first (better for MySQL syntax), then PostgreSQL, then SQLite
- **Error Handling**: Provides clear error messages for unsupported features
- **AST Structure**: sqlglot uses `from_` (with underscore) to avoid Python keyword conflict

**Code Flow**:

```python
def parse_sql(sql: str, dialect: Optional[str] = None):
    # Try dialects in order: mysql, postgres, sqlite
    for dialect_name in dialects_to_try:
        try:
            parsed = sqlglot.parse_one(sql, dialect=dialect_name)
            if isinstance(parsed, exp.Select):
                _validate_query(parsed)  # Check unsupported features
                return parsed
        except Exception:
            continue
    raise ParseError("Failed to parse SQL")
```

**Why Multiple Dialects?**

- Different databases have slightly different SQL syntax
- Auto-detection makes the library more flexible
- Falls back gracefully if one dialect fails

---

### 3. Planner (`planner.py`)

**Purpose**: Convert AST into a logical execution plan

**Output**: `LogicalPlan` dataclass containing:

- Root table and alias
- List of joins (with join type, keys)
- WHERE expression tree
- SELECT projections

**Extraction Logic**:

#### FROM Clause Extraction

```python
# sqlglot stores FROM as 'from_' (with underscore)
from_expr = ast.args.get("from_") or ast.args.get("from")
root_table, root_alias = _extract_table_and_alias(from_expr.this)
```

#### JOIN Extraction

For each JOIN in the query:

1. Extract join type (INNER, LEFT)
2. Extract table name and alias
3. Extract ON condition
4. Parse ON condition to get left and right join keys

**Join Key Parsing**:

```python
def _extract_join_keys(on_expr):
    # Only supports equality joins: alias1.col1 = alias2.col2
    if not isinstance(on_expr, exp.EQ):
        raise ParseError("Only equality joins supported")

    left = on_expr.this  # Left side of =
    right = on_expr.expression  # Right side of =

    # Convert to string format: "alias.column"
    left_key = _column_to_string(left)
    right_key = _column_to_string(right)

    return left_key, right_key
```

**Why This Design?**

- Separates parsing from execution
- Makes it easier to optimize/transform plans later
- Clear data structure for execution

---

### 4. Executor (`executor.py`)

**Purpose**: Build iterator pipeline from logical plan

**Pipeline Construction**:

1. Start with `ScanIterator` for root table
2. Add `FilterIterator` if WHERE clause exists
3. Add join iterators for each JOIN (in order)
4. Add `ProjectIterator` for SELECT projection

**Join Strategy Selection**:

```python
def _build_join_iterator(left_iterator, join_info, sources, source_metadata):
    # Check if right side is sorted by join key
    right_ordered_by = source_metadata.get("ordered_by")

    if right_ordered_by matches join_key:
        return MergeJoinIterator(...)  # More efficient
    else:
        return LookupJoinIterator(...)  # Loads table into memory
```

**Why This Order?**

- Filters applied early reduce data volume
- Joins happen in SQL order (no reordering yet)
- Projection last minimizes data transfer

---

## Execution Model

### Iterator Protocol

All operators implement Python's iterator protocol:

- `__iter__()`: Returns self
- `__next__()`: Returns next row or raises `StopIteration`

**Benefits**:

- Lazy evaluation: Only processes rows as needed
- Memory efficient: One row in memory at a time
- Composable: Operators chain together naturally

### Operator Chain Example

```
ScanIterator → FilterIterator → LookupJoinIterator → ProjectIterator
     ↓              ↓                    ↓                  ↓
  [row1]        [row1]              [row1+row2]        [selected cols]
  [row2]        [row2]              [row2+row3]        [selected cols]
  [row3]        [row3]              [row3+row4]        [selected cols]
```

Each operator pulls from the previous one using `next()`.

---

## Join Algorithms

### 1. LookupJoinIterator

**Algorithm**: Hash-based lookup join

**When Used**: Default for most joins

**How It Works**:

1. **Build Phase** (in `__init__`):

   ```python
   def _build_index(self):
       # Load entire right table into memory
       for row in self.right_source_fn():
           key_value = row[join_key_column]
           if key_value not in self.lookup_index:
               self.lookup_index[key_value] = []
           self.lookup_index[key_value].append(row)
   ```

   - Creates dictionary: `{join_key: [matching_rows]}`
   - Handles duplicate keys (one key → multiple rows)

2. **Probe Phase** (in `__next__`):

   ```python
   def __next__(self):
       left_row = next(self.left_source)
       left_key = left_row[left_join_key]

       # Lookup matching right rows
       right_matches = self.lookup_index.get(left_key, [])

       if INNER JOIN and no matches:
           continue  # Skip this left row

       if LEFT JOIN and no matches:
           return left_row + NULLs

       # Yield cross-product of matches
       return left_row + right_matches[current_index]
   ```

**Time Complexity**:

- Build: O(R) where R = size of right table
- Probe: O(1) per lookup (average case)
- Total: O(R + L) where L = size of left table

**Space Complexity**: O(R) - entire right table in memory

**Why This Design?**

- Simple to implement
- Fast lookups (O(1) average)
- Handles duplicate keys naturally
- Works for any join key type

**Limitations**:

- Loads entire right table into memory
- Not efficient for very large right tables
- No index usage (just Python dict)

---

### 2. MergeJoinIterator

**Algorithm**: Merge join (requires sorted inputs)

**When Used**: When both sides are sorted by join key

**How It Works**:

1. **Advance Both Sides**:

   ```python
   def __next__(self):
       # Get left row
       left_row = next(self.left_source)
       left_key = get_key(left_row)

       # Advance right until keys match or pass
       while right_key < left_key:
           advance_right()

       if right_key == left_key:
           # Keys match - collect all rows with same key
           fill_right_buffer(left_key)
           return combine(left_row, right_buffer[current])
   ```

2. **Handle Duplicate Keys**:
   - When keys match, collect all rows with same key from both sides
   - Produce cross-product of matching rows
   - Advance to next key

**Time Complexity**: O(R + L) - single pass through both tables

**Space Complexity**: O(K) where K = max duplicate key run size (usually very small)

**Why This Design?**

- Very memory efficient (only buffers equal-key runs)
- Fast for sorted data
- No need to load entire table

**Requirements**:

- Both sides must be sorted by join key
- Must specify `ordered_by` when registering source

**When to Use**:

- Large right tables (can't fit in memory)
- Data already sorted
- Memory-constrained environments

---

## Expression Evaluation

### Evaluator (`evaluator.py`)

**Purpose**: Evaluate SQL expressions against row data

**Supported Expressions**:

1. **Column References**:

   ```python
   if isinstance(expr, exp.Column):
       col_name = f"{expr.table}.{expr.name}"  # "alias.column"
       return row[col_name]
   ```

2. **Comparisons** (`=`, `!=`, `<`, `>`, `<=`, `>=`):

   ```python
   if isinstance(expr, exp.EQ):
       left = evaluate_expression(expr.this, row)
       right = evaluate_expression(expr.expression, row)
       return left == right
   ```

3. **Boolean Logic** (`AND`, `OR`, `NOT`):

   ```python
   if isinstance(expr, exp.And):
       left = evaluate_expression(expr.this, row)
       if not left:  # Short-circuit evaluation
           return False
       right = evaluate_expression(expr.expression, row)
       return bool(right)
   ```

4. **NULL Checks** (`IS NULL`, `IS NOT NULL`):

   ```python
   if isinstance(expr, exp.Is):
       value = evaluate_expression(expr.this, row)
       if expr.expression is None or isinstance(expr.expression, exp.Null):
           return value is None
   ```

5. **IN Clauses**:
   ```python
   if isinstance(expr, exp.In):
       left = evaluate_expression(expr.this, row)
       values = [evaluate_expression(e, row) for e in expr.expression.expressions]
       return left in values
   ```

**Evaluation Strategy**:

- Recursive tree traversal
- Bottom-up evaluation (leaves first, then parents)
- Short-circuit for AND/OR (performance optimization)

**Why Recursive?**

- Handles nested expressions naturally
- Matches AST structure
- Easy to extend with new expression types

---

## Data Flow

### Complete Example Flow

**Query**:

```sql
SELECT users.name, departments.name AS dept_name
FROM users
JOIN departments ON users.dept_id = departments.id
WHERE users.active = 1
```

**Step-by-Step Execution**:

1. **Parser**:

   ```
   SQL String → AST (sqlglot.Select)
   ```

2. **Planner**:

   ```
   AST → LogicalPlan {
       root_table: "users",
       joins: [JoinInfo(table="departments", left_key="users.dept_id", right_key="departments.id")],
       where_expr: EQ(Column("users.active"), Literal(1)),
       projections: [Column("users.name"), Alias(Column("departments.name"), "dept_name")]
   }
   ```

3. **Executor** builds pipeline:

   ```
   ScanIterator(users)
   → FilterIterator(WHERE users.active = 1)
   → LookupJoinIterator(departments)
   → ProjectIterator(SELECT name, dept_name)
   ```

4. **Execution**:

   ```
   Row 1: {"users.id": 1, "users.dept_id": 10, "users.active": 1}
   → Filter: passes (active = 1)
   → Join: lookup dept_id=10 → {"departments.id": 10, "departments.name": "Engineering"}
   → Project: {"name": "Alice", "dept_name": "Engineering"}
   → YIELD

   Row 2: {"users.id": 2, "users.dept_id": 20, "users.active": 0}
   → Filter: fails (active = 0)
   → SKIP
   ```

---

## Design Decisions

### 1. Why Iterator-Based?

**Decision**: Use Python iterators instead of loading full tables

**Rationale**:

- **Memory Efficiency**: Process one row at a time
- **Lazy Evaluation**: Only compute what's needed
- **Composability**: Operators chain naturally
- **Pythonic**: Fits Python's iterator protocol

**Trade-offs**:

- ✅ Low memory usage
- ✅ Can handle very large datasets
- ❌ More complex code
- ❌ Can't easily rewind/backtrack

---

### 2. Why Two Join Algorithms?

**Decision**: Implement both lookup and merge joins

**Rationale**:

- **Lookup Join**: Simple, works for any data, fast for small right tables
- **Merge Join**: Memory efficient, works for large right tables, requires sorted data

**Selection Logic**:

```python
if right_table_is_sorted_by_join_key:
    use_merge_join()  # Memory efficient
else:
    use_lookup_join()  # Simple and fast
```

**Trade-offs**:

- ✅ Flexibility: Choose best algorithm per join
- ✅ Handles both small and large tables
- ❌ More code to maintain
- ❌ User must specify `ordered_by` for merge joins

---

### 3. Why Row-by-Row Processing?

**Decision**: Process one row at a time instead of batches

**Rationale**:

- **Streaming**: Results available immediately
- **Memory**: Constant memory usage
- **Simplicity**: Easier to reason about

**Trade-offs**:

- ✅ Low memory footprint
- ✅ Immediate results
- ❌ More function call overhead
- ❌ Can't optimize across rows

---

### 4. Why Separate Parser/Planner/Executor?

**Decision**: Three-phase architecture

**Rationale**:

- **Separation of Concerns**: Each phase has clear responsibility
- **Testability**: Can test each phase independently
- **Extensibility**: Easy to add optimizations between phases
- **Debugging**: Clear boundaries for debugging

**Alternative Considered**: Single-phase execution

- ❌ Harder to test
- ❌ Harder to optimize
- ❌ Less flexible

---

### 5. Why Dictionary Row Representation?

**Decision**: Use `Dict[str, Any]` for rows

**Rationale**:

- **Flexibility**: Can handle any schema
- **Readability**: Column names as keys
- **Pythonic**: Natural Python data structure

**Alternative Considered**: Named tuples or classes

- ❌ Less flexible (fixed schema)
- ❌ More code
- ✅ Better performance (but not critical here)

**Column Naming Convention**:

- Prefixed with table alias: `"alias.column"`
- Prevents column name conflicts in joins
- Example: `{"users.id": 1, "users.name": "Alice", "departments.name": "Engineering"}`

---

## Code Structure

### Module Organization

```
streaming_sql_engine/
├── __init__.py          # Public API exports
├── engine.py            # Main Engine class
├── parser.py            # SQL parsing
├── planner.py           # Logical plan construction
├── executor.py          # Execution pipeline builder
├── operators.py         # Iterator operators (Scan, Filter, Join, Project)
├── evaluator.py         # Expression evaluation
└── db_connector.py      # Database connection utilities
```

### Key Data Structures

#### LogicalPlan

```python
@dataclass
class LogicalPlan:
    root_table: str
    root_alias: Optional[str]
    joins: List[JoinInfo]
    where_expr: Optional[exp.Expression]
    projections: List[exp.Expression]
```

#### JoinInfo

```python
@dataclass
class JoinInfo:
    table: str
    alias: Optional[str]
    join_type: str  # "INNER" or "LEFT"
    left_key: str   # "alias.column"
    right_key: str  # "alias.column"
```

### Operator Hierarchy

All operators inherit from nothing (just implement iterator protocol):

```
Iterator Protocol
├── ScanIterator          # Reads from source
├── FilterIterator        # Filters rows
├── LookupJoinIterator    # Hash-based join
├── MergeJoinIterator     # Merge-based join
└── ProjectIterator       # Selects/renames columns
```

**Why No Base Class?**

- Python's duck typing: "If it quacks like an iterator, it's an iterator"
- Simpler code
- No unnecessary abstraction

---

## Performance Characteristics

### Time Complexity

| Operation           | Complexity | Notes                                |
| ------------------- | ---------- | ------------------------------------ |
| Scan                | O(N)       | N = table size                       |
| Filter              | O(N)       | Must check every row                 |
| Lookup Join (build) | O(R)       | R = right table size                 |
| Lookup Join (probe) | O(L)       | L = left table size, O(1) per lookup |
| Merge Join          | O(R + L)   | Single pass through both             |
| Project             | O(N)       | N = number of rows                   |

### Space Complexity

| Operation   | Complexity | Notes                                     |
| ----------- | ---------- | ----------------------------------------- |
| Scan        | O(1)       | One row at a time                         |
| Filter      | O(1)       | One row at a time                         |
| Lookup Join | O(R)       | Entire right table in memory              |
| Merge Join  | O(K)       | K = max duplicate key run (usually small) |
| Project     | O(1)       | One row at a time                         |

### Memory Usage Patterns

**Lookup Join**:

- Builds hash table of right table: `O(R)` memory
- Best for: Small right tables (< 1GB)
- Worst for: Very large right tables

**Merge Join**:

- Buffers equal-key runs: `O(K)` memory where K << R
- Best for: Large right tables, sorted data
- Worst for: Unsorted data (can't use)

**Overall Pipeline**:

- Most operators: O(1) memory (one row)
- Only lookup joins materialize data
- Total memory: Sum of all lookup-joined right tables

---

## Extension Points

### Adding New Operators

1. Create class implementing iterator protocol:

```python
class CustomIterator:
    def __init__(self, source):
        self.source = source

    def __iter__(self):
        return self

    def __next__(self):
        row = next(self.source)
        # Transform row
        return transformed_row
```

2. Add to executor pipeline:

```python
# In executor.py
iterator = CustomIterator(iterator)
```

### Adding New Expression Types

1. Add to evaluator:

```python
# In evaluator.py
elif isinstance(expr, exp.NewExpressionType):
    # Evaluate new expression
    return result
```

### Adding New Join Types

1. Create new join iterator class
2. Add selection logic in `_build_join_iterator()`
3. Handle join semantics (e.g., RIGHT JOIN, FULL OUTER)

---

## Testing Strategy

### Unit Tests

- Test each operator independently
- Mock source iterators
- Verify output for various inputs

### Integration Tests

- Test full query execution
- Use real database connections (test database)
- Verify results match database queries

### Performance Tests

- Measure memory usage
- Time execution for various data sizes
- Compare with database joins

---

## Future Improvements

### Potential Optimizations

1. **Query Optimization**:

   - Reorder joins (smallest first)
   - Push filters earlier
   - Cost-based join selection

2. **Caching**:

   - Cache lookup tables
   - Reuse across queries

3. **Parallelism**:

   - Parallel join building
   - Parallel filtering

4. **Index Support**:
   - Use database indexes for filtering
   - Index-aware join selection

### Unsupported Features (Future)

- GROUP BY and aggregations
- ORDER BY
- Subqueries
- UNION
- Non-equality joins
- Arithmetic expressions

---

## Conclusion

The Streaming SQL Engine is designed for **flexibility over performance**. It enables:

- Joining data from different sources
- Memory-efficient processing
- Streaming results
- Python-based query execution

It trades performance (10-100x slower than databases) for flexibility (can join any data sources).

The architecture is modular, extensible, and follows Python best practices for iterator-based processing.
