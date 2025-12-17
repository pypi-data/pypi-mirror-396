#!/usr/bin/env python
"""
Pre-release comprehensive test suite for streaming-sql-engine 1.0.0
Tests all core functionality before release.
"""

import sys
import traceback
from typing import List, Tuple

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results: List[Tuple[str, bool, str]] = []

def test(name: str):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            try:
                func()
                tests_passed += 1
                test_results.append((name, True, ""))
                print(f"✓ {name}")
                return True
            except Exception as e:
                tests_failed += 1
                error_msg = str(e)
                test_results.append((name, False, error_msg))
                print(f"✗ {name}: {error_msg}")
                if "--verbose" in sys.argv:
                    traceback.print_exc()
                return False
        return wrapper
    return decorator

# ============================================================================
# TEST SUITE
# ============================================================================

@test("Import Engine")
def test_import_engine():
    """Test that Engine can be imported"""
    from streaming_sql_engine import Engine
    assert Engine is not None

@test("Engine initialization (default)")
def test_engine_init_default():
    """Test Engine initialization with defaults"""
    from streaming_sql_engine import Engine
    engine = Engine()
    assert engine.use_polars == False, "Default should be False"
    assert engine.debug == False

@test("Engine initialization (use_polars=True)")
def test_engine_init_polars():
    """Test Engine initialization with use_polars=True"""
    from streaming_sql_engine import Engine
    engine = Engine(use_polars=True)
    assert engine.use_polars == True

@test("Engine initialization (use_polars=False)")
def test_engine_init_no_polars():
    """Test Engine initialization with use_polars=False"""
    from streaming_sql_engine import Engine
    engine = Engine(use_polars=False)
    assert engine.use_polars == False

@test("Register simple source")
def test_register_source():
    """Test registering a simple source"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def simple_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", simple_source)
    assert "users" in engine._sources

@test("Simple SELECT query")
def test_simple_select():
    """Test a simple SELECT query"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
        ])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT users.name, users.age FROM users"))
    
    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[0]["age"] == 30

@test("SELECT with WHERE clause")
def test_select_where():
    """Test SELECT with WHERE clause"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35},
        ])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT users.name FROM users WHERE users.age > 28"))
    
    assert len(results) == 2
    names = [r["name"] for r in results]
    assert "Alice" in names
    assert "Charlie" in names
    assert "Bob" not in names

@test("INNER JOIN query")
def test_inner_join():
    """Test INNER JOIN between two sources"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ])
    
    def orders_source():
        return iter([
            {"id": 1, "user_id": 1, "product": "Book"},
            {"id": 2, "user_id": 2, "product": "Pen"},
        ])
    
    engine.register("users", users_source)
    engine.register("orders", orders_source)
    
    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "INNER JOIN orders ON users.id = orders.user_id"
    ))
    
    assert len(results) == 2
    assert results[0]["name"] == "Alice"
    assert results[0]["product"] == "Book"

@test("LEFT JOIN query")
def test_left_join():
    """Test LEFT JOIN query"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 3, "name": "Charlie"},
        ])
    
    def orders_source():
        return iter([
            {"id": 1, "user_id": 1, "product": "Book"},
        ])
    
    engine.register("users", users_source)
    engine.register("orders", orders_source)
    
    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "LEFT JOIN orders ON users.id = orders.user_id"
    ))
    
    assert len(results) == 3
    # Alice has order
    alice = [r for r in results if r["name"] == "Alice"][0]
    assert alice["product"] == "Book"
    # Bob and Charlie have no orders
    bob = [r for r in results if r["name"] == "Bob"][0]
    assert bob["product"] is None

@test("Column aliasing")
def test_column_aliasing():
    """Test column aliasing in SELECT"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT users.name AS user_name FROM users"))
    
    assert len(results) == 1
    assert "user_name" in results[0]
    assert results[0]["user_name"] == "Alice"

@test("Table aliasing")
def test_table_aliasing():
    """Test table aliasing"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT u.name FROM users AS u"))
    
    assert len(results) == 1
    assert results[0]["name"] == "Alice"

@test("Multiple joins")
def test_multiple_joins():
    """Test query with multiple joins"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    def orders_source():
        return iter([{"id": 1, "user_id": 1, "product_id": 1}])
    
    def products_source():
        return iter([{"id": 1, "name": "Book"}])
    
    engine.register("users", users_source)
    engine.register("orders", orders_source)
    engine.register("products", products_source)
    
    results = list(engine.query(
        "SELECT users.name, products.name AS product_name "
        "FROM users "
        "INNER JOIN orders ON users.id = orders.user_id "
        "INNER JOIN products ON orders.product_id = products.id"
    ))
    
    assert len(results) == 1
    assert results[0]["name"] == "Alice"
    assert results[0]["product_name"] == "Book"

@test("Empty result set")
def test_empty_result():
    """Test query that returns no results"""
    from streaming_sql_engine import Engine
    engine = Engine()
    
    def users_source():
        return iter([])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT users.name FROM users"))
    
    assert len(results) == 0

@test("Version check")
def test_version():
    """Test that version is accessible"""
    from streaming_sql_engine import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)
    # Should be semantic version format
    parts = __version__.split(".")
    assert len(parts) >= 2

@test("Polars optional (when not available)")
def test_polars_optional():
    """Test that engine works without Polars"""
    from streaming_sql_engine import Engine
    engine = Engine(use_polars=False)
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", users_source)
    results = list(engine.query("SELECT users.name FROM users"))
    
    assert len(results) == 1

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests"""
    print("=" * 70)
    print("STREAMING SQL ENGINE - PRE-RELEASE TEST SUITE")
    print("=" * 70)
    print()
    
    # Run all tests
    test_import_engine()
    test_engine_init_default()
    test_engine_init_polars()
    test_engine_init_no_polars()
    test_register_source()
    test_simple_select()
    test_select_where()
    test_inner_join()
    test_left_join()
    test_column_aliasing()
    test_table_aliasing()
    test_multiple_joins()
    test_empty_result()
    test_version()
    test_polars_optional()
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print()
    
    if tests_failed > 0:
        print("FAILED TESTS:")
        for name, passed, error in test_results:
            if not passed:
                print(f"  - {name}: {error}")
        print()
        return 1
    
    print("✓ All tests passed! Ready for 1.0.0 release.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
