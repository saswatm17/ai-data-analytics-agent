import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = "data/ecommerce.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        region TEXT,
        signup_date TEXT
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL
    );

    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        sale_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    );
    """)

    regions = ["North", "South", "East", "West"]
    customers = [
        (i, f"Customer_{i}", f"user{i}@email.com",
         random.choice(regions),
         (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"))
        for i in range(1, 51)
    ]

    categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
    products = [
        (i, f"Product_{i}", random.choice(categories), round(random.uniform(10, 500), 2))
        for i in range(1, 21)
    ]

    sales = [
        (i, random.randint(1, 50), random.randint(1, 20),
         random.randint(1, 5),
         (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))).strftime("%Y-%m-%d"))
        for i in range(1, 201)
    ]

    cursor.executemany("INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?)", customers)
    cursor.executemany("INSERT OR IGNORE INTO products VALUES (?,?,?,?)", products)
    cursor.executemany("INSERT OR IGNORE INTO sales VALUES (?,?,?,?,?)", sales)

    conn.commit()
    conn.close()
    print("✅ Database initialized with dummy data.")

if __name__ == "__main__":
    init_db()