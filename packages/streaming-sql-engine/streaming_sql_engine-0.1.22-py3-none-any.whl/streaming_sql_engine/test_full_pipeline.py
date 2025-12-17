#!/usr/bin/env python
"""Test full pipeline to see what's happening"""

from streaming_sql_engine import Engine

engine = Engine(debug=True)
def users_source():
    return iter([
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ])
engine.register("users", users_source)

print("Testing WHERE clause:")
print("=" * 60)
results = list(engine.query("SELECT users.name FROM users WHERE users.age > 28"))
print(f"\nFinal results: {results}")
print(f"Count: {len(results)}")
