"""
Генерация тестовых данных для MS SQL Server.
Использование:
    python generate_data.py 1000
    python generate_data.py 10000
    python generate_data.py 100000
"""
import sys
import random
import pymssql
from faker import Faker
from db_config import MSSQL_CONFIG

fake = Faker("ru_RU")

ORDERS_PER_USER = 5
ITEMS_PER_ORDER = 3


def get_conn():
    return pymssql.connect(**MSSQL_CONFIG)


def clear_tables(cur):
    # Отключаем constraint проверки для быстрой очистки
    cur.execute("DELETE FROM order_items")
    cur.execute("DELETE FROM orders")
    cur.execute("DELETE FROM products")
    cur.execute("DELETE FROM users")
    # Сбрасываем IDENTITY счётчики
    cur.execute("DBCC CHECKIDENT ('order_items', RESEED, 0)")
    cur.execute("DBCC CHECKIDENT ('orders',      RESEED, 0)")
    cur.execute("DBCC CHECKIDENT ('products',    RESEED, 0)")
    cur.execute("DBCC CHECKIDENT ('users',       RESEED, 0)")
    print("🗑  Таблицы очищены.")


def generate(users_count: int):
    products_count = users_count
    conn = get_conn()
    cur = conn.cursor()

    clear_tables(cur)
    conn.commit()

    # --- Пользователи ---
    print(f"👤 Генерация {users_count:,} пользователей...")
    batch = []
    for i in range(users_count):
        batch.append((fake.name(), fake.unique.ascii_email()))
        if len(batch) == 500 or i == users_count - 1:
            cur.executemany(
                "INSERT INTO users (name, email) VALUES (%s, %s)", batch
            )
            conn.commit()
            batch = []

    cur.execute("SELECT id FROM users")
    user_ids = [r[0] for r in cur.fetchall()]

    # --- Товары ---
    print(f"📦 Генерация {products_count:,} товаров...")
    batch = []
    for i in range(products_count):
        batch.append((fake.word(), round(random.uniform(10, 500), 2)))
        if len(batch) == 500 or i == products_count - 1:
            cur.executemany(
                "INSERT INTO products (name, price) VALUES (%s, %s)", batch
            )
            conn.commit()
            batch = []

    cur.execute("SELECT id FROM products")
    product_ids = [r[0] for r in cur.fetchall()]

    # --- Заказы ---
    total_orders = users_count * ORDERS_PER_USER
    print(f"🛒 Генерация {total_orders:,} заказов...")
    batch = [(uid,) for uid in user_ids for _ in range(ORDERS_PER_USER)]
    for i in range(0, len(batch), 1000):
        cur.executemany("INSERT INTO orders (user_id) VALUES (%s)", batch[i:i+1000])
        conn.commit()

    cur.execute("SELECT id FROM orders")
    order_ids = [r[0] for r in cur.fetchall()]

    # --- Позиции заказов ---
    print(f"📋 Генерация {total_orders * ITEMS_PER_ORDER:,} позиций...")
    item_batch = []
    for oid in order_ids:
        for _ in range(ITEMS_PER_ORDER):
            item_batch.append((
                oid,
                random.choice(product_ids),
                random.randint(1, 5)
            ))
        if len(item_batch) >= 2000:
            cur.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity) "
                "VALUES (%s, %s, %s)", item_batch
            )
            conn.commit()
            item_batch = []

    if item_batch:
        cur.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity) "
            "VALUES (%s, %s, %s)", item_batch
        )
        conn.commit()

    cur.close()
    conn.close()

    print("\n✅ Готово! Создано:")
    print(f"   — {users_count:,} пользователей")
    print(f"   — {products_count:,} товаров")
    print(f"   — {total_orders:,} заказов")
    print(f"   — {total_orders * ITEMS_PER_ORDER:,} позиций в заказах")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    generate(n)
