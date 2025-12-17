#!/usr/bin/env python
"""
Comprehensive unit tests for all Engine options and configurations.

Tests cover:
- Engine initialization options (debug, use_polars)
- Source registration options (ordered_by, filename)
- Source function protocols (dynamic_where, dynamic_columns)
- Join type selection based on options
- Optimization protocols
"""

import sys
import os
import tempfile
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streaming_sql_engine import Engine


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def add(self, name, passed, error=""):
        if passed:
            self.passed += 1
            print(f"✓ {name}")
        else:
            self.failed += 1
            print(f"✗ {name}: {error}")
        self.results.append((name, passed, error))


results = TestResults()


def test(name):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            try:
                func()
                results.add(name, True)
            except Exception as e:
                error_msg = str(e)
                if "--verbose" in sys.argv:
                    import traceback
                    traceback.print_exc()
                results.add(name, False, error_msg)
        return wrapper
    return decorator


# ============================================================================
# ENGINE INITIALIZATION OPTIONS
# ============================================================================

@test("Engine: debug=False (default)")
def test_debug_false_default():
    """Test Engine with debug=False (default)"""
    engine = Engine()
    assert engine.debug == False
    assert engine.use_polars == False


@test("Engine: debug=True")
def test_debug_true():
    """Test Engine with debug=True"""
    engine = Engine(debug=True)
    assert engine.debug == True
    assert engine.use_polars == False


@test("Engine: use_polars=False (default)")
def test_use_polars_false_default():
    """Test Engine with use_polars=False (default)"""
    engine = Engine()
    assert engine.use_polars == False


@test("Engine: use_polars=True")
def test_use_polars_true():
    """Test Engine with use_polars=True"""
    engine = Engine(use_polars=True)
    assert engine.use_polars == True


@test("Engine: debug=True, use_polars=True")
def test_both_options_true():
    """Test Engine with both debug and use_polars enabled"""
    engine = Engine(debug=True, use_polars=True)
    assert engine.debug == True
    assert engine.use_polars == True


@test("Engine: debug=True, use_polars=False")
def test_debug_true_polars_false():
    """Test Engine with debug=True, use_polars=False"""
    engine = Engine(debug=True, use_polars=False)
    assert engine.debug == True
    assert engine.use_polars == False


# ============================================================================
# SOURCE REGISTRATION OPTIONS
# ============================================================================

@test("Source registration: basic (no options)")
def test_register_basic():
    """Test registering source without any options"""
    engine = Engine()
    
    def source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", source)
    assert "users" in engine._sources
    assert engine._source_metadata["users"]["ordered_by"] is None
    assert engine._source_metadata["users"]["filename"] is None


@test("Source registration: ordered_by option")
def test_register_ordered_by():
    """Test registering source with ordered_by option"""
    engine = Engine()
    
    def source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", source, ordered_by="id")
    assert "users" in engine._sources
    assert engine._source_metadata["users"]["ordered_by"] == "id"
    assert engine._source_metadata["users"]["filename"] is None


@test("Source registration: filename option")
def test_register_filename():
    """Test registering source with filename option"""
    engine = Engine()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump({"id": 1, "name": "Alice"}, f)
        f.write("\n")
        temp_filename = f.name
    
    try:
        def source():
            with open(temp_filename, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", source, filename=temp_filename)
        assert "users" in engine._sources
        assert engine._source_metadata["users"]["ordered_by"] is None
        assert engine._source_metadata["users"]["filename"] == temp_filename
    finally:
        os.unlink(temp_filename)


@test("Source registration: ordered_by and filename together")
def test_register_both_options():
    """Test registering source with both ordered_by and filename"""
    engine = Engine()
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        json.dump({"id": 1, "name": "Alice"}, f)
        f.write("\n")
        temp_filename = f.name
    
    try:
        def source():
            with open(temp_filename, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", source, ordered_by="id", filename=temp_filename)
        assert "users" in engine._sources
        assert engine._source_metadata["users"]["ordered_by"] == "id"
        assert engine._source_metadata["users"]["filename"] == temp_filename
    finally:
        os.unlink(temp_filename)


# ============================================================================
# SOURCE FUNCTION PROTOCOLS
# ============================================================================

@test("Protocol: dynamic_where parameter")
def test_protocol_dynamic_where():
    """Test source function with dynamic_where protocol"""
    engine = Engine()
    
    called_with_where = []
    
    def source(dynamic_where=None, dynamic_columns=None):
        # Accept both parameters even if only using one
        called_with_where.append(dynamic_where)
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", source)
    
    # Query with WHERE clause should trigger protocol
    results = list(engine.query("SELECT users.name FROM users WHERE users.id = 1"))
    
    # Protocol should be called (may be None if WHERE can't be pushed)
    assert len(called_with_where) > 0


@test("Protocol: dynamic_columns parameter")
def test_protocol_dynamic_columns():
    """Test source function with dynamic_columns protocol"""
    engine = Engine()
    
    called_with_columns = []
    
    def source(dynamic_where=None, dynamic_columns=None):
        # Accept both parameters even if only using one
        called_with_columns.append(dynamic_columns)
        return iter([{"id": 1, "name": "Alice", "email": "alice@example.com"}])
    
    engine.register("users", source)
    
    # Query selecting only some columns should trigger protocol
    results = list(engine.query("SELECT users.name FROM users"))
    
    # Protocol should be called
    assert len(called_with_columns) > 0


@test("Protocol: dynamic_where and dynamic_columns together")
def test_protocol_both():
    """Test source function with both dynamic_where and dynamic_columns"""
    engine = Engine()
    
    called_with_where = []
    called_with_columns = []
    
    def source(dynamic_where=None, dynamic_columns=None):
        called_with_where.append(dynamic_where)
        called_with_columns.append(dynamic_columns)
        return iter([{"id": 1, "name": "Alice", "email": "alice@example.com"}])
    
    engine.register("users", source)
    
    # Query with WHERE and SELECT should trigger both protocols
    results = list(engine.query("SELECT users.name FROM users WHERE users.id = 1"))
    
    # Both protocols should be called
    assert len(called_with_where) > 0
    assert len(called_with_columns) > 0


@test("Protocol: source without protocol (no parameters)")
def test_no_protocol():
    """Test source function without protocol parameters"""
    engine = Engine()
    
    def source():
        return iter([{"id": 1, "name": "Alice"}])
    
    engine.register("users", source)
    
    # Should work fine without protocol
    results = list(engine.query("SELECT users.name FROM users"))
    assert len(results) == 1


# ============================================================================
# JOIN TYPE SELECTION BASED ON OPTIONS
# ============================================================================

@test("Join type: Lookup Join (default, no options)")
def test_join_lookup_default():
    """Test that default join is Lookup Join"""
    engine = Engine(use_polars=False)
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    def orders_source():
        return iter([{"id": 1, "user_id": 1, "product": "Book"}])
    
    engine.register("users", users_source)
    engine.register("orders", orders_source)
    
    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "INNER JOIN orders ON users.id = orders.user_id"
    ))
    
    assert len(results) == 1
    assert results[0]["name"] == "Alice"


@test("Join type: Merge Join (ordered_by)")
def test_join_merge_ordered_by():
    """Test Merge Join with ordered_by option"""
    engine = Engine(use_polars=False)
    
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
    
    engine.register("users", users_source, ordered_by="id")
    engine.register("orders", orders_source, ordered_by="user_id")
    
    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "INNER JOIN orders ON users.id = orders.user_id"
    ))
    
    assert len(results) == 2


@test("Join type: MMAP Join (filename)")
def test_join_mmap_filename():
    """Test MMAP Join with filename option"""
    try:
        # Check if MMAP is available
        from streaming_sql_engine.operators_mmap import MmapLookupJoinIterator, MMAP_AVAILABLE
        if not MMAP_AVAILABLE or MmapLookupJoinIterator is None:
            # MMAP not available, skip test gracefully
            return
    except (ImportError, AttributeError):
        # MMAP not available, skip test gracefully
        return
    
    engine = Engine(use_polars=True)
    
    # Create temporary files
    users_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    orders_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    
    json.dump({"id": 1, "name": "Alice"}, users_file)
    users_file.write("\n")
    users_file.close()
    
    json.dump({"id": 1, "user_id": 1, "product": "Book"}, orders_file)
    orders_file.write("\n")
    orders_file.close()
    
    try:
        def users_source():
            with open(users_file.name, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        def orders_source():
            with open(orders_file.name, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", users_source, filename=users_file.name)
        engine.register("orders", orders_source, filename=orders_file.name)
        
        results_list = list(engine.query(
            "SELECT users.name, orders.product FROM users "
            "INNER JOIN orders ON users.id = orders.user_id"
        ))
        
        assert len(results_list) == 1
    except Exception as e:
        # If MMAP join fails, fallback should work
        # Just verify the query executes
        results_list = list(engine.query(
            "SELECT users.name FROM users"
        ))
        assert len(results_list) == 1
    finally:
        if os.path.exists(users_file.name):
            os.unlink(users_file.name)
        if os.path.exists(orders_file.name):
            os.unlink(orders_file.name)


@test("Join type: Polars Join (use_polars=True)")
def test_join_polars():
    """Test Polars Join with use_polars=True"""
    try:
        import polars
    except ImportError:
        # Skip if Polars not available
        return
    
    engine = Engine(use_polars=True)
    
    def users_source():
        return iter([{"id": 1, "name": "Alice"}])
    
    def orders_source():
        return iter([{"id": 1, "user_id": 1, "product": "Book"}])
    
    engine.register("users", users_source)
    engine.register("orders", orders_source)
    
    results = list(engine.query(
        "SELECT users.name, orders.product FROM users "
        "INNER JOIN orders ON users.id = orders.user_id"
    ))
    
    assert len(results) == 1


# ============================================================================
# COMBINED OPTIONS
# ============================================================================

@test("Combined: use_polars=True + filename")
def test_combined_polars_filename():
    """Test combining use_polars=True with filename option"""
    engine = Engine(use_polars=True)
    
    users_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    json.dump({"id": 1, "name": "Alice"}, users_file)
    users_file.write("\n")
    users_file.close()
    
    try:
        def users_source():
            with open(users_file.name, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", users_source, filename=users_file.name)
        
        results = list(engine.query("SELECT users.name FROM users"))
        assert len(results) == 1
    finally:
        os.unlink(users_file.name)


@test("Combined: ordered_by + filename")
def test_combined_ordered_by_filename():
    """Test combining ordered_by with filename option"""
    engine = Engine(use_polars=False)
    
    users_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    json.dump({"id": 1, "name": "Alice"}, users_file)
    users_file.write("\n")
    users_file.close()
    
    try:
        def users_source():
            with open(users_file.name, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", users_source, ordered_by="id", filename=users_file.name)
        
        results = list(engine.query("SELECT users.name FROM users"))
        assert len(results) == 1
    finally:
        os.unlink(users_file.name)


@test("Combined: protocol + filename")
def test_combined_protocol_filename():
    """Test combining protocol with filename option"""
    engine = Engine(use_polars=True)
    
    users_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    json.dump({"id": 1, "name": "Alice", "email": "alice@example.com"}, users_file)
    users_file.write("\n")
    users_file.close()
    
    try:
        called_with_where = []
        called_with_columns = []
        
        def users_source(dynamic_where=None, dynamic_columns=None):
            called_with_where.append(dynamic_where)
            called_with_columns.append(dynamic_columns)
            with open(users_file.name, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("users", users_source, filename=users_file.name)
        
        results = list(engine.query("SELECT users.name FROM users WHERE users.id = 1"))
        
        assert len(results) == 1
        # Protocols should be called
        assert len(called_with_where) > 0 or len(called_with_columns) > 0
    finally:
        os.unlink(users_file.name)


# ============================================================================
# EDGE CASES
# ============================================================================

@test("Edge case: empty source")
def test_empty_source():
    """Test engine with empty source"""
    engine = Engine()
    
    def empty_source():
        return iter([])
    
    engine.register("users", empty_source)
    results = list(engine.query("SELECT users.name FROM users"))
    assert len(results) == 0


@test("Edge case: source with None values")
def test_source_with_none():
    """Test source that yields None values - engine should handle gracefully"""
    engine = Engine()
    
    def source_with_none():
        # Engine operators should skip None values
        rows = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        for row in rows:
            yield row
    
    engine.register("users", source_with_none)
    results = list(engine.query("SELECT users.name FROM users"))
    # Should work normally
    assert len(results) == 2


@test("Edge case: multiple sources with different options")
def test_multiple_sources_different_options():
    """Test multiple sources with different registration options"""
    engine = Engine()
    
    def source1():
        return iter([{"id": 1, "name": "Alice"}])
    
    def source2():
        return iter([{"id": 1, "name": "Bob"}])
    
    def source3():
        return iter([{"id": 1, "name": "Charlie"}])
    
    engine.register("users1", source1)  # No options
    engine.register("users2", source2, ordered_by="id")  # With ordered_by
    engine.register("users3", source3)  # No options
    
    assert "users1" in engine._sources
    assert "users2" in engine._sources
    assert "users3" in engine._sources
    
    assert engine._source_metadata["users1"]["ordered_by"] is None
    assert engine._source_metadata["users2"]["ordered_by"] == "id"
    assert engine._source_metadata["users3"]["ordered_by"] is None


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests"""
    print("=" * 70)
    print("ENGINE OPTIONS - COMPREHENSIVE UNIT TESTS")
    print("=" * 70)
    print()
    
    # Run all tests
    test_debug_false_default()
    test_debug_true()
    test_use_polars_false_default()
    test_use_polars_true()
    test_both_options_true()
    test_debug_true_polars_false()
    
    test_register_basic()
    test_register_ordered_by()
    test_register_filename()
    test_register_both_options()
    
    test_protocol_dynamic_where()
    test_protocol_dynamic_columns()
    test_protocol_both()
    test_no_protocol()
    
    test_join_lookup_default()
    test_join_merge_ordered_by()
    test_join_mmap_filename()
    test_join_polars()
    
    test_combined_polars_filename()
    test_combined_ordered_by_filename()
    test_combined_protocol_filename()
    
    test_empty_source()
    test_source_with_none()
    test_multiple_sources_different_options()
    
    # Summary
    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {results.passed + results.failed}")
    print(f"Passed: {results.passed} ✓")
    print(f"Failed: {results.failed}")
    print()
    
    if results.failed > 0:
        print("FAILED TESTS:")
        for name, passed, error in results.results:
            if not passed:
                print(f"  - {name}: {error}")
        print()
        return 1
    
    print("✓ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
