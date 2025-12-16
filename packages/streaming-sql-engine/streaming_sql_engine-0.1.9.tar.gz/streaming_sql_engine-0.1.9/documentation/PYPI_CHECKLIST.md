# PyPI Publishing Checklist

## ✅ Pre-Publishing Checklist

### 1. Package Configuration

- [x] `setup.py` configured with proper metadata
- [x] `pyproject.toml` configured (modern standard)
- [x] `MANIFEST.in` created to include necessary files
- [x] `LICENSE` file created (MIT License)
- [x] `README.md` is complete and well-formatted
- [x] `requirements.txt` includes all dependencies

### 2. Metadata Updates Needed

- [ ] Update `author` in `setup.py` and `pyproject.toml`
- [ ] Update `author_email` in both files
- [ ] Update `url` with your GitHub repository URL
- [ ] Update `version` number (use semantic versioning)

### 3. Code Quality

- [x] Package structure is correct
- [x] `__init__.py` exports main classes
- [x] All imports work correctly
- [ ] Code is tested (if you have tests)
- [ ] Documentation is complete

### 4. Files Created

- [x] `setup.py` - Package configuration
- [x] `pyproject.toml` - Modern package config
- [x] `MANIFEST.in` - File inclusion rules
- [x] `LICENSE` - MIT License
- [x] `PUBLISHING.md` - Detailed publishing guide
- [x] `QUICK_PUBLISH.md` - Quick reference
- [x] `PYPI_CHECKLIST.md` - This file

## 📦 Publishing Steps

### Step 1: Install Build Tools

```bash
pip install --upgrade build twine
```

### Step 2: Update Metadata

Edit `setup.py` and `pyproject.toml`:

- Replace "Your Name" with your name
- Replace "your.email@example.com" with your email
- Replace "yourusername" with your GitHub username
- Update version if needed

### Step 3: Clean & Build

```bash
# Remove old builds
rm -rf build/ dist/ *.egg-info

# Build package
python -m build
```

### Step 4: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ rivulet
```

### Step 5: Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

**Security Tip**: Use API token instead of password:

1. Go to https://pypi.org/manage/account/token/
2. Create new API token
3. Username: `__token__`
4. Password: your token

### Step 6: Verify

```bash
pip install rivulet
python -c "from streaming_sql_engine import Engine; print('Success!')"
```

## 🔄 Updating the Package

When publishing a new version:

1. **Update version** in:

   - `__init__.py` (`__version__ = "0.1.1"`)
   - `setup.py` (`version = "0.1.1"`)
   - `pyproject.toml` (`version = "0.1.1"`)

2. **Rebuild and upload**:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## 📝 Current Package Info

- **Package Name**: `rivulet`
- **Current Version**: `0.1.0`
- **Python Requirements**: `>=3.8`
- **License**: MIT

## 🔗 Useful Links

- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **PyPI Account**: https://pypi.org/account/register/
- **API Tokens**: https://pypi.org/manage/account/token/

## 📚 Documentation

- **Detailed Guide**: See [PUBLISHING.md](PUBLISHING.md)
- **Quick Reference**: See [QUICK_PUBLISH.md](QUICK_PUBLISH.md)

## ⚠️ Important Notes

1. **Version Numbers**: Must be unique and follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Test First**: Always test on TestPyPI before publishing to production PyPI
3. **Security**: Use API tokens, not passwords
4. **Metadata**: Keep author info and URLs up to date

## ✅ Ready to Publish?

Once you've:

1. Updated all metadata (author, email, URLs)
2. Tested the build locally
3. Created PyPI account
4. (Optional) Tested on TestPyPI

You're ready to publish! Follow the steps above.
