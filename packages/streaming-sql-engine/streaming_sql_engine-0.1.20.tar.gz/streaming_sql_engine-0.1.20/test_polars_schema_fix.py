"""
Direct test of Polars schema inference and duplicate column fixes.
"""

import json
import tempfile
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from streaming_sql_engine import Engine

def test_schema_inference_fix():
    """Test that mixed types (string/numeric) don't cause schema inference errors."""
    print("=" * 70)
    print("TEST 1: Schema Inference Fix (Mixed Types)")
    print("=" * 70)
    
    # Create data with mixed types - some prices as strings, some as numbers
    mixed_data = [
        {"id": 1, "price": "14.95", "name": "Product 1"},  # String price
        {"id": 2, "price": 15.50, "name": "Product 2"},     # Numeric price
        {"id": 3, "price": "20.00", "name": "Product 3"},   # String price
        {"id": 4, "price": 25.75, "name": "Product 4"},     # Numeric price
    ]
    
    # Create JSONL file
    test_file = "test_mixed_types.jsonl"
    with open(test_file, 'w') as f:
        for record in mixed_data:
            f.write(json.dumps(record) + '\n')
    
    try:
        engine = Engine(debug=False, use_polars=True)
        
        def load_data():
            with open(test_file, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("products", load_data, filename=test_file)
        
        # Query that uses Polars join (will trigger schema inference)
        query = """
            SELECT p1.id, p1.price, p2.price AS other_price
            FROM products p1
            JOIN products p2 ON p1.id = p2.id
        """
        
        results = list(engine.query(query))
        print(f"[OK] Query executed successfully: {len(results)} rows")
        print(f"[OK] No schema inference errors!")
        return True
        
    except Exception as e:
        if "could not append value" in str(e) or "infer_schema_length" in str(e):
            print(f"[FAILED] Schema inference error still occurs: {e}")
            return False
        else:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

def test_duplicate_column_fix():
    """Test that duplicate column selections don't cause errors."""
    print("\n" + "=" * 70)
    print("TEST 2: Duplicate Column Name Fix")
    print("=" * 70)
    
    # Create simple data
    data = [
        {"id": 1, "price": "10.00", "name": "Product 1"},
        {"id": 2, "price": "20.00", "name": "Product 2"},
    ]
    
    test_file = "test_duplicate.jsonl"
    with open(test_file, 'w') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
    
    try:
        engine = Engine(debug=False, use_polars=True)
        
        def load_data():
            with open(test_file, 'r') as f:
                for line in f:
                    if line.strip():
                        yield json.loads(line)
        
        engine.register("products", load_data, filename=test_file)
        
        # Query with duplicate column selection (same column selected twice)
        query = """
            SELECT 
                products.price,
                products.price AS price_alias,
                products.id
            FROM products
        """
        
        results = list(engine.query(query))
        print(f"[OK] Query executed successfully: {len(results)} rows")
        print(f"[OK] No duplicate column name errors!")
        
        # Verify results have correct columns
        if results:
            row = results[0]
            print(f"[OK] Result columns: {list(row.keys())}")
            if 'price' in row and 'price_alias' in row:
                print(f"[OK] Both 'price' and 'price_alias' present in results")
            else:
                print(f"[WARNING] Expected columns not found")
        
        return True
        
    except Exception as e:
        if "duplicate output name" in str(e) or "duplicate column" in str(e):
            print(f"[FAILED] Duplicate column error still occurs: {e}")
            return False
        else:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test1 = test_schema_inference_fix()
    test2 = test_duplicate_column_fix()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Schema Inference Fix: {'PASSED' if test1 else 'FAILED'}")
    print(f"Duplicate Column Fix: {'PASSED' if test2 else 'FAILED'}")
    
    sys.exit(0 if (test1 and test2) else 1)

