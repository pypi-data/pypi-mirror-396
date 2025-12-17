#!/usr/bin/env python
"""Debug failing tests"""

from streaming_sql_engine import Engine

# Test WHERE clause
print("=" * 60)
print("TEST 1: WHERE clause")
print("=" * 60)
engine = Engine()
def users_source():
    return iter([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ])
engine.register("users", users_source)
results = list(engine.query("SELECT users.name FROM users WHERE users.age > 28"))
print(f"Results: {results}")
print(f"Count: {len(results)}")
print(f"Expected: 2 (Alice and Charlie)")
print()

# Test LEFT JOIN
print("=" * 60)
print("TEST 2: LEFT JOIN")
print("=" * 60)
engine2 = Engine()
def users_source2():
    return iter([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ])
def orders_source():
    return iter([
        {"id": 1, "user_id": 1, "product": "Book"},
    ])
engine2.register("users", users_source2)
engine2.register("orders", orders_source)
results2 = list(engine2.query(
    "SELECT users.name, orders.product FROM users "
    "LEFT JOIN orders ON users.id = orders.user_id"
))
print(f"Results: {results2}")
print(f"Count: {len(results2)}")
print(f"Expected: 3 (Alice, Bob, Charlie)")
