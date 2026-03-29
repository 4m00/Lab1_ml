"""
Создание тестовой базы данных orm_test и таблиц в MS SQL Server.
Запуск: python create_tables.py
"""
import pymssql
from db_config import MSSQL_CONFIG


def get_conn(database=None):
    cfg = dict(MSSQL_CONFIG)
    if database:
        cfg["database"] = database
    return pymssql.connect(**cfg)


def create_database():
    """Создаём БД orm_test если не существует."""
    # Подключаемся к master, чтобы создать новую БД
    conn = pymssql.connect(
        server=MSSQL_CONFIG["server"],
        port=MSSQL_CONFIG["port"],
        user=MSSQL_CONFIG["user"],
        password=MSSQL_CONFIG["password"],
        database="master",
        autocommit=True,
    )
    cur = conn.cursor()
    cur.execute("""
        IF NOT EXISTS (
            SELECT name FROM sys.databases WHERE name = 'orm_test'
        )
        CREATE DATABASE orm_test
    """)
    cur.close()
    conn.close()
    print("✅ База данных orm_test готова.")


CREATE_SQL = """
-- Удаляем таблицы если существуют (в правильном порядке)
IF OBJECT_ID('order_items', 'U') IS NOT NULL DROP TABLE order_items;
IF OBJECT_ID('orders',      'U') IS NOT NULL DROP TABLE orders;
IF OBJECT_ID('products',    'U') IS NOT NULL DROP TABLE products;
IF OBJECT_ID('users',       'U') IS NOT NULL DROP TABLE users;

CREATE TABLE users (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    created_at DATETIME2   DEFAULT GETDATE()
);

CREATE TABLE products (
    id    INT IDENTITY(1,1) PRIMARY KEY,
    name  VARCHAR(255)   NOT NULL,
    price NUMERIC(10,2)  NOT NULL
);

CREATE TABLE orders (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    user_id    INT      NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    created_at DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE order_items (
    id         INT IDENTITY(1,1) PRIMARY KEY,
    order_id   INT NOT NULL REFERENCES orders(id)   ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id),
    quantity   INT NOT NULL
);

CREATE INDEX idx_orders_user_id          ON orders(user_id);
CREATE INDEX idx_order_items_order_id    ON order_items(order_id);
CREATE INDEX idx_order_items_product_id  ON order_items(product_id);
"""


def create_tables():
    conn = get_conn(database="orm_test")
    # MS SQL не поддерживает несколько DDL в одном execute — разбиваем по GO
    cur = conn.cursor()
    for statement in CREATE_SQL.split(";"):
        stmt = statement.strip()
        if stmt:
            cur.execute(stmt)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблицы успешно созданы: users, products, orders, order_items")


if __name__ == "__main__":
    create_database()
    create_tables()
