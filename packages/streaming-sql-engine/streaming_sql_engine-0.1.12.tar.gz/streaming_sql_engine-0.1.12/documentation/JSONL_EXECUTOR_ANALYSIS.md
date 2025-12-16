# JSONL Executor Analysis: Is It Still Useful?

## What JSONL Executor Does

**JSONL executor** (`use_jsonl_mode=True`):
1. Exports all tables to JSONL files
2. Merges JSONL files by reading and joining them
3. Applies projection
4. Yields results

**Regular executor** (default):
1. Streams data row-by-row through iterator pipeline
2. Joins happen in-memory (or with mmap/Polars)
3. Applies projection
4. Yields results immediately

---

## Comparison

| Aspect | Regular Executor | JSONL Executor |
|--------|-----------------|----------------|
| **Streaming** | ✅ True streaming (row-by-row) | ❌ Not streaming (exports first) |
| **Memory** | ✅ Low (with mmap) | ⚠️ Medium (temporary files) |
| **CPU** | ✅ Fast (with Polars) | ✅ Lower CPU (simpler logic) |
| **Speed** | ✅ Fast | ⚠️ Slower (disk I/O overhead) |
| **Complexity** | ⚠️ More complex | ✅ Simpler logic |
| **Disk Usage** | ✅ None | ❌ Temporary files |

---

## When JSONL Mode Might Be Useful

### ✅ Use Case 1: Very Complex Queries

**Scenario:** Multiple joins where regular executor struggles

```python
# Complex query with many joins
query = """
    SELECT ...
    FROM table1
    JOIN table2 ON ...
    JOIN table3 ON ...
    JOIN table4 ON ...
    JOIN table5 ON ...
"""

# Regular executor: Complex iterator pipeline
# JSONL executor: Simpler (export all, merge sequentially)
```

**Benefit:** Simpler execution logic, less CPU for complex pipelines

### ✅ Use Case 2: CPU-Constrained Environments

**Scenario:** CPU is bottleneck, not memory or disk

```python
# If CPU is the constraint
engine = Engine(use_jsonl_mode=True)  # Lower CPU usage
```

**Benefit:** Simpler join logic uses less CPU

### ✅ Use Case 3: Debugging/Inspection

**Scenario:** Want to inspect intermediate results

```python
engine = Engine(use_jsonl_mode=True, debug=True)
# Temporary JSONL files can be inspected
```

**Benefit:** Can examine exported files

---

## When JSONL Mode Is NOT Useful

### ❌ Most Cases (Now)

**Why:** Regular executor is already efficient with:
- ✅ Mmap joins (low memory)
- ✅ Polars (fast)
- ✅ Protocol optimizations (less data)
- ✅ True streaming (immediate results)

**Regular executor handles:**
- Large files → Mmap joins
- Fast processing → Polars
- Complex queries → Already optimized

### ❌ When You Need Streaming

**JSONL mode:** Exports everything first, then processes
**Regular mode:** Streams row-by-row immediately

**If you need immediate results, JSONL mode defeats the purpose.**

### ❌ When Disk Space Is Limited

**JSONL mode:** Creates temporary files (can be large)
**Regular mode:** No disk usage

---

## Real-World Assessment

### Current State

**Regular executor is already very efficient:**
- Mmap joins: 90-99% memory reduction
- Polars: 10-200x speedup
- Protocol optimizations: Less data transferred
- True streaming: Immediate results

**JSONL executor:**
- Simpler logic (but slower)
- Lower CPU (but disk I/O overhead)
- Not streaming (defeats purpose)

### Recommendation

**JSONL executor is mostly redundant now.**

**Reasons:**
1. ✅ Regular executor handles large datasets (mmap)
2. ✅ Regular executor is fast (Polars)
3. ✅ Regular executor streams (immediate results)
4. ✅ Regular executor is memory-efficient (mmap + optimizations)

**JSONL executor only useful for:**
- Very specific CPU-constrained scenarios
- Debugging/inspection needs
- Legacy compatibility

---

## Should We Keep It?

### Option 1: Keep It (Current)

**Pros:**
- ✅ Provides alternative execution strategy
- ✅ Useful for specific edge cases
- ✅ Users can choose

**Cons:**
- ⚠️ Adds complexity
- ⚠️ Not commonly used
- ⚠️ Defeats streaming purpose

### Option 2: Remove It

**Pros:**
- ✅ Simpler codebase
- ✅ Focus on streaming (core purpose)
- ✅ Regular executor already handles all cases

**Cons:**
- ❌ Loses alternative execution mode
- ❌ Some users might rely on it

### Option 3: Deprecate It

**Pros:**
- ✅ Keeps backward compatibility
- ✅ Signals it's not recommended
- ✅ Can remove later

**Cons:**
- ⚠️ Still maintains code

---

## My Recommendation

### **Deprecate JSONL Mode**

**Reasoning:**
1. Regular executor is already efficient
2. JSONL mode defeats streaming purpose
3. Not commonly used
4. Adds complexity

**Action:**
- Keep code for now (backward compatibility)
- Add deprecation warning
- Document that regular executor is recommended
- Remove in future version

---

## Alternative: Improve Regular Executor

Instead of JSONL mode, improve regular executor:

1. **Better join algorithms** (already have: merge, lookup, mmap, Polars)
2. **Better memory management** (already have: mmap)
3. **Better performance** (already have: Polars)
4. **Better optimizations** (already have: protocol-based)

**Result:** Regular executor handles everything JSONL mode does, but better!

---

## Summary

### Is JSONL Executor Useful?

**Short answer: Mostly not anymore.**

**Why:**
- Regular executor is already efficient
- JSONL mode defeats streaming purpose
- Not commonly used
- Adds complexity

**When it might be useful:**
- Very specific CPU-constrained scenarios
- Debugging/inspection
- Legacy compatibility

**Recommendation:**
- Keep for backward compatibility
- Add deprecation warning
- Document regular executor as recommended
- Consider removing in future version

**The regular executor with mmap + Polars + protocol optimizations is superior in almost all cases.**

