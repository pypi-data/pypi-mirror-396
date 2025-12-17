# Quick Fix for join_required_columns Bug

## Problem
The installed version from PyPI (0.1.4) has a bug where `join_required_columns` is assigned inside an `if debug:` block but used outside, causing `UnboundLocalError` when `debug=False`.

## Solution 1: Patch Installed Version (Quick Fix)

Run this on your server:

```bash
# Download the patch script
# Or copy examples/patch_executor.py to your server

# Run the patch
python3 patch_executor.py
```

This will automatically fix the installed version.

## Solution 2: Update Package (Recommended)

Update to version 0.1.5 which has the fix:

```bash
pip install --upgrade streaming-sql-engine==0.1.5
```

## Solution 3: Manual Patch

If the automatic patch doesn't work, manually edit:

```bash
# Find the installed package
python3 -c "import streaming_sql_engine; print(streaming_sql_engine.__file__)"

# Edit the executor.py file
# Change line ~128-130 from:
#     if debug:
#         # Get required columns for joined table
#         join_required_columns = plan.required_columns.get(join_info.table)
#
# To:
#     # Get required columns for joined table (must be outside debug block!)
#     join_required_columns = plan.required_columns.get(join_info.table)
#     
#     if debug:
```

## What Was Fixed

- Moved `join_required_columns` assignment outside the `debug` block
- Fixed reconciliation script bug with `spryker_id_int` reference


