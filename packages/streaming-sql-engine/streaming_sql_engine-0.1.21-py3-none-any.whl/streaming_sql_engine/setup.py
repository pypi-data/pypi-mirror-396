"""
Setup script for streaming-sql-engine
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="streaming-sql-engine",
    version="0.1.21",
    author="Theodore Pantazopoulo",
    author_email="your.email@example.com",
    description="A lightweight SQL execution engine for streaming row-by-row queries with joins across multiple data sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ierofantis/streaming-sql-engine/tree/master",
    # Package structure: files are in root directory
    packages=["streaming_sql_engine"],
    package_dir={"streaming_sql_engine": "."},
    py_modules=[
        "streaming_sql_engine.engine",
        "streaming_sql_engine.executor",
        "streaming_sql_engine.parser",
        "streaming_sql_engine.planner",
        "streaming_sql_engine.optimizer",
        "streaming_sql_engine.evaluator",
        "streaming_sql_engine.operators",
        "streaming_sql_engine.operators_polars",
        "streaming_sql_engine.operators_mmap",
        "streaming_sql_engine.mmap_index",
        "streaming_sql_engine.polars_expression_translator",
        "streaming_sql_engine.protocol_helpers",
    ],
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "db": [
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
            "DBUtils>=3.0.0",
            "pymongo>=4.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "all": [
            "psycopg2-binary>=2.9.0",
            "pymysql>=1.0.0",
            "DBUtils>=3.0.0",
            "pymongo>=4.0.0",
        ],
    },
    keywords="sql streaming join database query engine",
    project_urls={
        "Bug Reports": "https://github.com/Ierofantis/streaming-sql-engine/issues",
        "Source": "https://github.com/Ierofantis/streaming-sql-engine/tree/master",
        "Documentation": "https://github.com/Ierofantis/streaming-sql-engine/tree/master#readme",
    },
)

