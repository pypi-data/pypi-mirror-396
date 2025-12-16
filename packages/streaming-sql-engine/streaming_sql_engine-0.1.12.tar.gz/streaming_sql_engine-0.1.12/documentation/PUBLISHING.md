# Publishing to PyPI

This guide explains how to publish the `rivulet` package to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **TestPyPI Account** (optional but recommended): Create an account at https://test.pypi.org/account/register/
3. **Build Tools**: Install build tools:
   ```bash
   pip install --upgrade build twine
   ```

## Step 1: Update Package Metadata

Before publishing, update the following files with your information:

1. **setup.py** or **pyproject.toml**:

   - Update `author` and `author_email`
   - Update `url` with your GitHub repository URL
   - Update version number (use semantic versioning: `MAJOR.MINOR.PATCH`)

2. **README.md**: Ensure it's complete and well-formatted

3. **LICENSE**: Ensure you have a LICENSE file (MIT License is recommended)

## Step 2: Prepare for Publishing

### Clean up the project:

```bash
# Remove build artifacts
rm -rf build/ dist/ *.egg-info

# Remove Python cache files
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Update version number:

Edit `__init__.py` and `setup.py`/`pyproject.toml` to update the version:

```python
# In __init__.py
__version__ = "0.1.0"

# In setup.py or pyproject.toml
version = "0.1.0"
```

## Step 3: Build the Package

### Build source distribution and wheel:

```bash
python -m build
```

This creates:

- `dist/rivulet-0.1.0.tar.gz` (source distribution)
- `dist/rivulet-0.1.0-py3-none-any.whl` (wheel)

### Verify the build:

```bash
# Check what files will be included
tar -tzf dist/rivulet-0.1.0.tar.gz | head -20
```

## Step 4: Test on TestPyPI (Recommended)

Before publishing to the real PyPI, test on TestPyPI:

### Upload to TestPyPI:

```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for your TestPyPI username and password.

### Test installation from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ rivulet
```

### Verify it works:

```python
from streaming_sql_engine import Engine
print(Engine.__module__)
```

## Step 5: Publish to PyPI

### Upload to PyPI:

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

**Note**: For better security, use an API token instead of password:

1. Go to https://pypi.org/manage/account/token/
2. Create a new API token
3. Use `__token__` as username and the token as password

### Verify publication:

Visit https://pypi.org/project/rivulet/ to see your package.

## Step 6: Install and Test

### Install from PyPI:

```bash
pip install rivulet
```

### Test installation:

```python
from streaming_sql_engine import Engine

engine = Engine()
print(f"Streaming SQL Engine version: {engine.__class__.__module__}")
```

## Updating the Package

When you need to publish a new version:

1. **Update version number** in:

   - `__init__.py` (`__version__`)
   - `setup.py` or `pyproject.toml` (`version`)

2. **Update CHANGELOG.md** (if you have one) with changes

3. **Build and upload**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Troubleshooting

### "Package already exists"

- The version number must be unique. Increment it in `setup.py`/`pyproject.toml` and `__init__.py`.

### "Invalid distribution"

- Ensure `MANIFEST.in` includes all necessary files
- Check that `README.md` exists and is valid Markdown

### "Module not found after installation"

- Verify `packages=find_packages()` in `setup.py` finds your package
- Check that `__init__.py` exists in your package directory

### "Missing dependencies"

- Ensure `requirements.txt` includes all dependencies
- Check that `install_requires` in `setup.py` matches `requirements.txt`

## Security Best Practices

1. **Use API tokens** instead of passwords for PyPI uploads
2. **Never commit** `.pypirc` file with credentials to git
3. **Use 2FA** on your PyPI account
4. **Test on TestPyPI** before publishing to production PyPI

## Additional Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)

## Quick Reference Commands

```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info

# Build package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install rivulet

# Install specific version
pip install rivulet==0.1.0
```
