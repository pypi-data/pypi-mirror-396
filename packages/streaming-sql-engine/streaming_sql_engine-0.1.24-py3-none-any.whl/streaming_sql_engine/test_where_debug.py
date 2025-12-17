#!/usr/bin/env python
"""Debug WHERE clause evaluation"""

from streaming_sql_engine.evaluator import evaluate_expression
from sqlglot import parse_one

# Test WHERE clause evaluation
row = {"users.id": 1, "users.name": "Alice", "users.age": 30}
expr = parse_one("users.age > 28")

print(f"Row: {row}")
print(f"Expression: {expr}")
print(f"Evaluated: {evaluate_expression(expr, row)}")

# Test with different age
row2 = {"users.id": 2, "users.name": "Bob", "users.age": 25}
print(f"\nRow2: {row2}")
print(f"Evaluated: {evaluate_expression(expr, row2)}")
