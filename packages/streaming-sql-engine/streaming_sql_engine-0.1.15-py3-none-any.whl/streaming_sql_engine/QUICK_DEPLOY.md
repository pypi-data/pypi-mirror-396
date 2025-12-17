# Quick PyPI Deployment Guide

## Prerequisites

Install build tools:
```bash
pip install build twine
```

## Step 1: Build the Package

```bash
# Clean old builds
rmdir /s /q build dist *.egg-info streaming_sql_engine.egg-info 2>nul

# Build package
python -m build
```

This creates:
- `dist/streaming-sql-engine-0.1.4.tar.gz`
- `dist/streaming-sql-engine-0.1.4-py3-none-any.whl`

## Step 2: Upload to PyPI

### Option A: Test on TestPyPI First (Recommended)

```bash
python -m twine upload --repository testpypi dist/*
```

Then test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ streaming-sql-engine
```

### Option B: Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for:
- **Username**: Your PyPI username (or `__token__` for API token)
- **Password**: Your PyPI password (or API token starting with `pypi-`)

## Step 3: Verify Installation

Wait a few minutes, then test:

```bash
pip install streaming-sql-engine

# Or with optional dependencies
pip install streaming-sql-engine[polars]
pip install streaming-sql-engine[db]
pip install streaming-sql-engine[all]

# Test import
python -c "from streaming_sql_engine import Engine, register_file_source; print('✅ Success!')"
```

## Using API Tokens (More Secure)

1. Go to https://pypi.org/manage/account/
2. Create API token
3. Use username: `__token__` and password: `pypi-...` (your token)

## Current Version: 0.1.4

Updated files:
- ✅ `pyproject.toml` - version 0.1.4
- ✅ `setup.py` - version 0.1.4  
- ✅ `__init__.py` - version 0.1.4

## What's New in 0.1.4

- Protocol helpers for automatic filter pushdown and column pruning
- WHERE clause pushdown to joined tables
- Improved performance with optimized protocol detection
- Better error handling and debugging


