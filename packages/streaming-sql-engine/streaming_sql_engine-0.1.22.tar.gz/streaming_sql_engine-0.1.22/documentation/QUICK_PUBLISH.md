# Quick PyPI Publishing Guide

## Prerequisites

```bash
pip install --upgrade build twine
```

## Steps

### 1. Update Metadata

Edit `setup.py` or `pyproject.toml`:

- Update `author` and `author_email`
- Update `url` with your GitHub repo
- Update `version` number

### 2. Clean & Build

```bash
# Clean old builds
rm -rf build/ dist/ *.egg-info

# Build package
python -m build
```

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ rivulet
```

### 4. Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

**Note**: Use PyPI API token for security:

- Go to https://pypi.org/manage/account/token/
- Create API token
- Username: `__token__`
- Password: your token

### 5. Verify

```bash
# Install from PyPI
pip install rivulet

# Test
python -c "from streaming_sql_engine import Engine; print('Success!')"
```

## Updating Version

1. Update version in `__init__.py` and `setup.py`/`pyproject.toml`
2. Rebuild and upload:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Files Created/Updated

- ✅ `setup.py` - Updated with better metadata
- ✅ `pyproject.toml` - Updated with all dependencies
- ✅ `MANIFEST.in` - Created to include necessary files
- ✅ `LICENSE` - Created MIT license file
- ✅ `PUBLISHING.md` - Detailed publishing guide
- ✅ `README.md` - Added PyPI installation instructions

## Next Steps

1. **Update author info** in `setup.py` and `pyproject.toml`
2. **Update GitHub URLs** in both files
3. **Create PyPI account** at https://pypi.org/account/register/
4. **Follow steps above** to publish

For detailed instructions, see [PUBLISHING.md](PUBLISHING.md).
