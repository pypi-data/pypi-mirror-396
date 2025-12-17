# How to Add This Library to Your Project

This document explains the different ways you can integrate the Streaming SQL Engine into your projects.

## Method 1: Install as Editable Package (Recommended)

**Best for:** Development, when you might modify the library

```bash
# In your project directory
cd /path/to/your/project

# Install the library in editable mode
pip install -e /path/to/sql_engine
```

**In your code:**

```python
from streaming_sql_engine import Engine, create_pool_from_env
# Use normally - no path manipulation needed
```

## Method 2: Add to Project's requirements.txt

**Best for:** Production deployments, team projects

### Step 1: Add to requirements.txt

```txt
# Local path (absolute)
streaming-sql-engine @ file:///absolute/path/to/sql_engine

# Or relative path (from project root)
streaming-sql-engine @ file://./libs/sql_engine

# Or from Git
streaming-sql-engine @ git+https://github.com/username/streaming-sql-engine.git
```

### Step 2: Install

```bash
pip install -r requirements.txt
```

## Method 3: Add to pyproject.toml (Modern Python Projects)

**Best for:** Projects using modern Python packaging

```toml
[project.dependencies]
streaming-sql-engine = {path = "../sql_engine", develop = true}
```

Then:

```bash
pip install -e .
```

## Method 4: Copy Library into Project

**Best for:** Simple projects, when you want everything in one place

### Project Structure:

```
my_project/
├── main.py
├── libs/
│   └── streaming_sql_engine/  # Copy the entire library here
│       ├── __init__.py
│       ├── engine.py
│       └── ...
└── requirements.txt
```

### In your code:

```python
import sys
import os

# Add libs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

from streaming_sql_engine import Engine
```

## Method 5: Use PYTHONPATH Environment Variable

**Best for:** Quick testing, when you don't want to install

```bash
# Linux/Mac
export PYTHONPATH=/path/to/sql_engine:$PYTHONPATH

# Windows (Command Prompt)
set PYTHONPATH=C:\path\to\sql_engine;%PYTHONPATH%

# Windows (PowerShell)
$env:PYTHONPATH = "C:\path\to\sql_engine;$env:PYTHONPATH"
```

Then in Python:

```python
from streaming_sql_engine import Engine
```

## Method 6: Install as System Package

**Best for:** Multiple projects using the same library

```bash
# Install globally (requires admin/sudo on some systems)
pip install /path/to/sql_engine

# Or with --user flag (no admin needed)
pip install --user /path/to/sql_engine
```

## Recommended Project Structure

```
my_project/
├── .env                    # Database credentials
├── main.py                 # Your main script
├── requirements.txt        # Project dependencies
├── libs/                   # Optional: local libraries
│   └── sql_engine/
└── src/                    # Your source code
    └── my_app/
        └── ...
```

## Example: Complete Setup

### 1. Create project structure

```bash
mkdir my_project
cd my_project
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
```

### 2. Create requirements.txt

```txt
streaming-sql-engine @ file:///path/to/sql_engine
python-dotenv>=1.0.0
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Create .env file

```env
db_host=localhost
db_port=5432
db_user=myuser
db_password=mypassword
db_name=mydatabase
```

### 5. Use in code

```python
# main.py
from streaming_sql_engine import Engine, create_pool_from_env, create_table_source
from dotenv import load_dotenv

load_dotenv()

pool = create_pool_from_env()
engine = Engine()

engine.register("users", create_table_source(pool, "users"))

for row in engine.query("SELECT * FROM users"):
    print(row)
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'streaming_sql_engine'"

**Solutions:**

1. Make sure you installed the package: `pip install -e /path/to/sql_engine`
2. Check your Python path: `python -c "import sys; print(sys.path)"`
3. Verify installation: `pip list | grep streaming`

### "ImportError: No module named 'sqlglot'"

**Solution:** Install dependencies:

```bash
pip install -r /path/to/sql_engine/requirements.txt
```

### Virtual Environment Issues

**Always use a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows
pip install -e /path/to/sql_engine
```

## Which Method Should I Use?

| Method           | When to Use                       |
| ---------------- | --------------------------------- |
| Editable Install | Development, modifying library    |
| requirements.txt | Production, team projects         |
| pyproject.toml   | Modern Python projects            |
| Copy to project  | Simple projects, no installation  |
| PYTHONPATH       | Quick testing, temporary use      |
| System install   | Multiple projects, shared library |

## Next Steps

- See [QUICK_START.md](QUICK_START.md) for usage examples
- Read [INSTALLATION.md](INSTALLATION.md) for detailed installation guide
- Check [README.md](README.md) for full documentation
