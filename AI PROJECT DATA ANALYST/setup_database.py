import sqlite3

# Database se connect karein (ye apne aap data.db file bana dega)
conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# 1. Products Table banayein
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)
''')

# 2. Kuch sample data bharein
products = [
    (1, 'Laptop', 50000),
    (2, 'Smartphone', 20000),
    (3, 'Tablet', 15000),
    (4, 'Headphones', 2000)
]

cursor.executemany('INSERT OR REPLACE INTO products VALUES (?,?,?)', products)

# Save karke close karein
conn.commit()
conn.close()

print("✅ Data.db fresh aur ready hai!")