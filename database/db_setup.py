import duckdb
import pandas as pd

# Connect to DB
conn = duckdb.connect("ecommerce.db")

# Dummy Data
customers = pd.DataFrame({
    "customer_id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "David"],
    "city": ["New York", "Los Angeles", "Chicago", "Houston"]
})

products = pd.DataFrame({
    "product_id": [101, 102, 103, 104],
    "product_name": ["Laptop", "Phone", "Tablet", "Headphones"],
    "price": [1000, 500, 300, 150]
})

orders = pd.DataFrame({
    "order_id": [1001, 1002, 1003, 1004],
    "customer_id": [1, 2, 3, 1],
    "product_id": [101, 102, 103, 104],
    "quantity": [1, 2, 1, 3]
})

# Create tables
conn.execute("CREATE TABLE IF NOT EXISTS customers AS SELECT * FROM customers")
conn.execute("CREATE TABLE IF NOT EXISTS products AS SELECT * FROM products")
conn.execute("CREATE TABLE IF NOT EXISTS orders AS SELECT * FROM orders")

print("✅ Database created successfully!")