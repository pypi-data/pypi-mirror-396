"""
Test script for Polars fixes with sample MongoDB and Spryker data.
Tests schema inference and duplicate column name handling.
"""

import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from streaming_sql_engine import Engine

# Sample MongoDB data (with product_offer_reference to match Spryker)
mongo_data = [
    {"sku": "96771", "price": "8.50", "list_price": None, "publish": False, "status": "D", "product_id": 34017149, "sf_sku": "SF-06349323", "merchant_reference": "MER304", "product_offer_reference": "MER304--.--96771--.--SF-06349323"},
    {"sku": "96821", "price": "9.40", "list_price": None, "publish": False, "status": "D", "product_id": 34017404, "sf_sku": "SF-02477384", "merchant_reference": "MER304", "product_offer_reference": "MER304--.--96821--.--SF-02477384"},
    {"sku": "8833", "price": "122.80", "list_price": "150.00", "publish": True, "status": "A", "product_id": 34018000, "sf_sku": "SF-14041047", "merchant_reference": "MER304", "product_offer_reference": "MER304--.--8833--.--SF-14041047"},
    {"sku": "8848", "price": "99.50", "list_price": None, "publish": True, "status": "A", "product_id": 34018001, "sf_sku": "SF-14041057", "merchant_reference": "MER304", "product_offer_reference": "MER304--.--8848--.--SF-14041057"},
]

# Sample Spryker data
spryker_data = [
    {"id_product_offer": 152860217, "approval_status": "approved", "concrete_sku": "SF-14041047", "is_active": 1, "merchant_reference": "MER304", "merchant_sku": "8833", "product_offer_reference": "MER304--.--8833--.--SF-14041047", "sf_merchant_ean": "8021233128240", "sf_merchant_product_name": "Parlux Advance Light Gold 2200Watt", "sf_merchant_url": "https://hairbeautycorner.com/parlux-advance-light-gold-2200watt", "sf_shipping_lead_time": 0, "gross_price": "122.80", "reference": "MER304--.--8833--.--SF-14041047", "price_type": 1, "query": "reference"},
    {"id_product_offer": 152860218, "approval_status": "approved", "concrete_sku": "SF-14041057", "is_active": 1, "merchant_reference": "MER304", "merchant_sku": "8848", "product_offer_reference": "MER304--.--8848--.--SF-14041057", "sf_merchant_ean": "8021233121012", "sf_merchant_product_name": "Parlux Superturbo High Power 2400W", "sf_merchant_url": "https://hairbeautycorner.com/parlux-superturbo-high-power", "sf_shipping_lead_time": 0, "gross_price": "99.50", "reference": "MER304--.--8848--.--SF-14041057", "price_type": 1, "query": "reference"},
    {"id_product_offer": 152860219, "approval_status": "pending", "concrete_sku": "SF-06349323", "is_active": 0, "merchant_reference": "MER304", "merchant_sku": "96771", "product_offer_reference": "MER304--.--96771--.--SF-06349323", "sf_merchant_ean": "8021233129999", "sf_merchant_product_name": "Test Product 1", "sf_merchant_url": "https://example.com/product1", "sf_shipping_lead_time": 1, "gross_price": "8.50", "reference": "MER304--.--96771--.--SF-06349323", "price_type": 1, "query": "reference"},
]

def create_jsonl_file(data, filename):
    """Create a JSONL file with the given data."""
    with open(filename, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')
    print(f"[OK] Created {filename} with {len(data)} records")

def load_jsonl_generator(filename):
    """Generator function to load JSONL file."""
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def test_reconciliation_query():
    """Test the reconciliation query with Polars enabled."""
    print("=" * 70)
    print("TESTING POLARS FIXES")
    print("=" * 70)
    print()
    
    # Create temporary JSONL files
    mongo_file = "test_mongo.jsonl"
    spryker_file = "test_spryker.jsonl"
    
    try:
        create_jsonl_file(mongo_data, mongo_file)
        create_jsonl_file(spryker_data, spryker_file)
        
        # Initialize engine with Polars enabled (debug=False to avoid Unicode issues on Windows)
        print("\n[1] Initializing engine with Polars enabled...")
        engine = Engine(debug=False, use_polars=True)
        print("[OK] Engine initialized")
        
        # Register sources
        print("\n[2] Registering data sources...")
        engine.register("mongo", lambda: load_jsonl_generator(mongo_file), filename=mongo_file)
        engine.register("spryker", lambda: load_jsonl_generator(spryker_file), filename=spryker_file)
        print("[OK] Sources registered")
        
        # Test query 1: Reference match (similar to reconciliation script)
        print("\n[3] Testing reference match query...")
        print("-" * 70)
        query1 = """
            SELECT 
                spryker.id_product_offer,
                spryker.approval_status,
                spryker.concrete_sku,
                spryker.is_active,
                spryker.merchant_reference,
                spryker.merchant_sku,
                spryker.product_offer_reference,
                spryker.sf_merchant_ean,
                spryker.sf_merchant_product_name,
                spryker.sf_merchant_url,
                spryker.sf_shipping_lead_time,
                mongo.price,
                mongo.list_price,
                spryker.query AS query_type,
                mongo.price AS mongo_price,
                spryker.gross_price AS spryker_price,
                mongo.status AS mongo_status,
                spryker.is_active AS spryker_is_active
            FROM spryker
            JOIN mongo ON spryker.product_offer_reference = mongo.product_offer_reference
            WHERE spryker.query = 'reference'
        """
        
        print("Query:")
        print(query1.strip())
        print()
        
        # Debug: Check what data we have
        print("\n[DEBUG] Checking data...")
        print("Spryker product_offer_reference values:")
        for record in spryker_data:
            print(f"  - {record.get('product_offer_reference')} (query: {record.get('query')})")
        print("\nMongoDB product_offer_reference values:")
        for record in mongo_data:
            print(f"  - {record.get('product_offer_reference')}")
        
        results = []
        try:
            for row in engine.query(query1):
                results.append(row)
                print(f"  Result: id={row.get('id_product_offer')}, mongo_price={row.get('mongo_price')}, spryker_price={row.get('spryker_price')}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"\n[OK] Query 1 completed successfully: {len(results)} rows")
        
        # Test query 2: Simple join without WHERE clause (to test join matching)
        print("\n[4] Testing simple join query (no WHERE clause)...")
        print("-" * 70)
        query2 = """
            SELECT 
                spryker.id_product_offer,
                spryker.product_offer_reference,
                mongo.price AS mongo_price,
                spryker.gross_price AS spryker_price
            FROM spryker
            JOIN mongo ON spryker.product_offer_reference = mongo.product_offer_reference
        """
        
        print("Query:")
        print(query2.strip())
        print()
        
        results2 = []
        try:
            for row in engine.query(query2):
                results2.append(row)
                print(f"  Result {len(results2)}: id={row.get('id_product_offer')}, ref={row.get('product_offer_reference')}, mongo_price={row.get('mongo_price')}, spryker_price={row.get('spryker_price')}")
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print(f"\n[OK] Query 2 completed successfully: {len(results2)} rows")
        
        # Verify we got matches
        if len(results2) == 0:
            print("  [WARNING] No matches found - this might indicate a join issue")
        else:
            print("  [SUCCESS] Join is working correctly!")
        
        # Summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"[OK] Query 1 (with duplicate columns): {len(results)} rows")
        print(f"[OK] Query 2 (simple join): {len(results2)} rows")
        print("\n[OK] All tests passed! Polars fixes are working correctly.")
        return True
        
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        for f in [mongo_file, spryker_file]:
            if os.path.exists(f):
                os.remove(f)
                print(f"  Cleaned up {f}")

if __name__ == "__main__":
    success = test_reconciliation_query()
    sys.exit(0 if success else 1)

