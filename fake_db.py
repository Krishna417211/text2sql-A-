"""
Fake store database (SQLite) for testing the text-to-SQL chat.

Tables: customers, products, orders
"""

import os
import random
import sqlite3

DB_PATH = "fake_store.db"


def seed_db(path: str = DB_PATH) -> None:
    """Create (or re-create) a fake store database with sample data."""
    random.seed(42)
    if os.path.exists(path):
        os.remove(path)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            country TEXT NOT NULL,
            signup_date TEXT NOT NULL
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL
        );
        """
    )

    first = ["Aarav", "Priya", "Liam", "Emma", "Noah", "Olivia", "Arjun", "Sara",
             "Mateo", "Yuki", "Fatima", "Chen", "Ravi", "Anna", "Omar"]
    last = ["Nair", "Sharma", "Smith", "Garcia", "Kim", "Khan", "Patel", "Rossi",
            "Tanaka", "Silva"]
    countries = ["India", "USA", "UK", "Germany", "Japan", "Brazil", "Canada"]

    customers = []
    for i in range(1, 41):
        name = f"{random.choice(first)} {random.choice(last)}"
        email = f"user{i}@example.com"
        signup = f"{random.choice([2024, 2025, 2026])}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
        customers.append((i, name, email, random.choice(countries), signup))
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", customers)

    products = [
        (1, "Wireless Mouse", "Electronics", 19.99, 120),
        (2, "Mechanical Keyboard", "Electronics", 69.50, 60),
        (3, "USB-C Hub", "Electronics", 34.00, 85),
        (4, "Noise Cancelling Headphones", "Electronics", 149.00, 40),
        (5, "Running Shoes", "Apparel", 89.99, 70),
        (6, "Cotton T-Shirt", "Apparel", 14.50, 200),
        (7, "Water Bottle", "Home", 12.00, 150),
        (8, "Desk Lamp", "Home", 27.75, 55),
        (9, "Notebook (Pack of 3)", "Stationery", 8.25, 300),
        (10, "Ballpoint Pens (10)", "Stationery", 5.40, 500),
    ]
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)

    statuses = ["delivered", "shipped", "pending", "cancelled"]
    orders = []
    for i in range(1, 201):
        orders.append((
            i,
            random.randint(1, 40),
            random.randint(1, 10),
            random.randint(1, 5),
            f"{random.choice([2025, 2026])}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
            random.choices(statuses, weights=[60, 20, 12, 8])[0],
        ))
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", orders)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_db()
    print(f"Created {DB_PATH}")
