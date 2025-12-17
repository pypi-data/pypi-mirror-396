# Deploying to PyPI

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional, for testing): https://test.pypi.org/account/register/
3. **Install build tools**:
   ```bash
   pip install build twine
   ```

## Step 1: Update Version

Before deploying, update the version in:
- `pyproject.toml` (version field)
- `setup.py` (version field)
- `__init__.py` (__version__ variable)

Current version: **0.1.4**

## Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf streaming_sql_engine.egg-info/
```

## Step 3: Build the Package

```bash
# Build source distribution and wheel
python -m build
```

This creates:
- `dist/streaming-sql-engine-0.1.4.tar.gz` (source distribution)
- `dist/streaming-sql-engine-0.1.4-py3-none-any.whl` (wheel)

## Step 4: Test the Build (Optional but Recommended)

### Test on TestPyPI first:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ streaming-sql-engine
```

### Test locally:

```bash
# Install from local build
pip install dist/streaming-sql-engine-0.1.4-py3-none-any.whl

# Test import
python -c "from streaming_sql_engine import Engine; print('✅ Import successful!')"
```

## Step 5: Upload to PyPI

### Option A: Upload to TestPyPI First (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: Your PyPI username
- Password: Your PyPI password (or API token)

### Option B: Upload Directly to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Step 6: Verify Installation

After uploading, wait a few minutes for PyPI to process, then test:

```bash
# Install from PyPI
pip install streaming-sql-engine

# Or with optional dependencies
pip install streaming-sql-engine[polars]
pip install streaming-sql-engine[db]
pip install streaming-sql-engine[all]

# Test import
python -c "from streaming_sql_engine import Engine, register_file_source; print('✅ Import successful!')"
```

## Using API Tokens (More Secure)

Instead of using your password, create an API token:

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Create a new token with scope "Entire account" or specific project
4. Use the token as username: `__token__` and password: `pypi-...` (the token)

## Troubleshooting

### "Package already exists"
- Increment version number in `pyproject.toml`, `setup.py`, and `__init__.py`

### "Invalid distribution"
- Make sure all required files are included
- Check `MANIFEST.in` includes necessary files
- Verify `pyproject.toml` is valid

### "Module not found" after installation
- Check `package_dir` in `setup.py` matches your structure
- Verify `__init__.py` is in the correct location
- Check that all Python files are included

## Quick Deploy Script

Create a `deploy.sh` script:

```bash
#!/bin/bash
set -e

echo "🧹 Cleaning old builds..."
rm -rf build/ dist/ *.egg-info streaming_sql_engine.egg-info/

echo "📦 Building package..."
python -m build

echo "📤 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Deployment complete!"
echo "Test with: pip install streaming-sql-engine"
```

Make it executable: `chmod +x deploy.sh`

## Version History

- **0.1.4** - Current version with protocol helpers and WHERE clause pushdown to joined tables
- **0.1.3** - Previous version
- **0.1.2** - Previous version
- **0.1.0** - Initial release



