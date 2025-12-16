# Installation Guide

This guide explains different ways to add the Streaming SQL Engine library to your project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation Methods

### Method 1: Install as Editable Package (Recommended for Development)

This is the best option if you're actively developing or modifying the library:

```bash
# Navigate to the library directory
cd /path/to/sql_engine

# Install in editable mode
pip install -e .
```

**Benefits:**

- Changes to the library code are immediately available
- No need to reinstall after code changes
- Library is properly installed and importable

### Method 2: Install as Regular Package

If you just want to use the library without modifying it:

```bash
cd /path/to/sql_engine
pip install .
```

### Method 3: Add to Your Project's Dependencies

#### Using requirements.txt

In your project's `requirements.txt`:

```
# Local path (absolute or relative)
streaming-sql-engine @ file:///path/to/sql_engine

# Or from Git repository
streaming-sql-engine @ git+https://github.com/yourusername/streaming-sql-engine.git
```

Then install:

```bash
pip install -r requirements.txt
```

#### Using pyproject.toml

In your project's `pyproject.toml`:

```toml
[project.dependencies]
streaming-sql-engine = {path = "../sql_engine", develop = true}
```

### Method 4: Use Without Installation (Quick Start)

If you don't want to install the package, you can add it to your Python path:

```python
import sys
import os

# Add the library directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'path/to/sql_engine'))

from streaming_sql_engine import Engine
```

Or set the `PYTHONPATH` environment variable:

```bash
# Linux/Mac
export PYTHONPATH=/path/to/sql_engine:$PYTHONPATH

# Windows
set PYTHONPATH=C:\path\to\sql_engine;%PYTHONPATH%
```

## Verify Installation

After installation, verify it works:

```python
from streaming_sql_engine import Engine

engine = Engine()
print("✓ Library installed successfully!")
```

## Troubleshooting

### Import Error: No module named 'streaming_sql_engine'

**Solution:** Make sure you've installed the package:

```bash
pip install -e .
```

Or check that the library directory is in your Python path.

### Import Error: No module named 'sqlglot' or 'psycopg2'

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Permission Denied Error

**Solution:** Use `--user` flag or a virtual environment:

```bash
pip install --user -e .
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
pip install -e .
```

## Using in Different Projects

### Project Structure Example

```
my_project/
├── main.py
├── requirements.txt
└── libs/
    └── sql_engine/  # The streaming SQL engine library
        ├── streaming_sql_engine/
        ├── setup.py
        └── ...
```

In `requirements.txt`:

```
streaming-sql-engine @ file://./libs/sql_engine
```

### Virtual Environment Best Practice

Always use a virtual environment for your projects:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Install the library
cd libs/sql_engine
pip install -e .

# Or install from requirements.txt
cd ../..
pip install -r requirements.txt
```

## Development Setup

For contributing to the library:

```bash
# Clone or navigate to the library
cd sql_engine

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if configured)
pre-commit install
```
