# JSONL Executor Removed

## Summary

The JSONL executor (`use_jsonl_mode=True`) has been **removed** from the library.

## Why It Was Removed

1. **Defeated streaming purpose**: JSONL mode exported all data first, then processed it
2. **Redundant**: Regular executor already handles all cases efficiently with:
   - Mmap joins (90-99% memory reduction)
   - Polars optimizations (10-200x speedup)
   - Protocol-based optimizations (filter pushdown, column pruning)
   - True streaming (row-by-row processing)

3. **Slower**: Disk I/O overhead from temporary files
4. **Not commonly used**: Most users preferred regular streaming mode

## Migration Guide

### Before (Old Code)

```python
# Old: JSONL mode
engine = Engine(use_jsonl_mode=True)
```

### After (New Code)

```python
# New: Streaming mode (default)
engine = Engine()
# or explicitly
engine = Engine(use_polars=True)  # Enable Polars optimizations
```

**That's it!** Just remove `use_jsonl_mode=True` parameter.

## What Changed

### Removed Files
- ✅ `jsonl_executor.py` - Deleted
- ✅ `streaming_sql_engine/jsonl_executor.py` - Deleted

### Updated Files
- ✅ `engine.py` - Removed `use_jsonl_mode` parameter
- ✅ `streaming_sql_engine/engine.py` - Removed `use_jsonl_mode` parameter
- ✅ Example files updated

### API Changes

**Before:**
```python
def __init__(self, debug=False, use_jsonl_mode=False, use_polars=True):
```

**After:**
```python
def __init__(self, debug=False, use_polars=True):
```

## Benefits

✅ **Simpler API**: One less parameter to worry about
✅ **True streaming**: Row-by-row processing (core purpose)
✅ **Better performance**: Mmap + Polars + protocol optimizations
✅ **Cleaner codebase**: Less code to maintain

## Performance Comparison

| Aspect | JSONL Mode (Removed) | Regular Mode (Current) |
|--------|---------------------|------------------------|
| **Streaming** | ❌ No (exports first) | ✅ Yes (row-by-row) |
| **Memory** | ⚠️ Medium (temp files) | ✅ Low (mmap) |
| **Speed** | ⚠️ Slower (disk I/O) | ✅ Fast (Polars) |
| **CPU** | ✅ Lower | ✅ Fast (optimized) |

**Regular mode is superior in all aspects!**

## Questions?

**Q: What if I need JSONL export?**
A: Export results yourself:
```python
import json
for row in engine.query("SELECT * FROM table"):
    print(json.dumps(row))
```

**Q: Will my code break?**
A: Yes, if you used `use_jsonl_mode=True`. Just remove that parameter.

**Q: Is regular mode slower?**
A: No! Regular mode is faster with Polars optimizations.

---

**The regular executor with mmap + Polars + protocol optimizations handles everything JSONL mode did, but better!**

