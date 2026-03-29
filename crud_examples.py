"""
Лабораторная работа №1, Часть 1.
CRUD-операции: SQLAlchemy ORM, Django ORM, Raw SQL (MS SQL Server)
"""
import pymssql
from sqlalchemy.orm import sessionmaker
from models_sqlalchemy import get_engine, User, Product, Order, OrderItem
from db_config import MSSQL_CONFIG

engine  = get_engine()
Session = sessionmaker(bind=engine)


# ============================================================
#  SQLAlchemy CRUD
# ============================================================
def sqlalchemy_crud():
    print("\n" + "=" * 60)
    print("🔷 SQLAlchemy ORM — CRUD операции")
    print("=" * 60)
    session = Session()
    try:
        # CREATE
        user = User(name="Иван Иванов", email="ivan_crud@example.com")
        session.add(user)
        session.flush()
        print(f"✅ CREATE: пользователь id={user.id}")

        product = Product(name="Тестовый товар", price=999.99)
        session.add(product)
        session.flush()
        print(f"✅ CREATE: товар id={product.id}")

        order = Order(user_id=user.id)
        session.add(order)
        session.flush()
        session.add(OrderItem(order_id=order.id,
                              product_id=product.id, quantity=2))
        session.flush()
        print(f"✅ CREATE: заказ id={order.id} с позицией")

        # READ
        found = session.query(User).filter(User.id == user.id).first()
        print(f"✅ READ:   {found.name} / {found.email}")

        top3 = session.query(User).order_by(User.name).limit(3).all()
        print(f"✅ READ:   первые 3 — {[u.name for u in top3]}")

        # UPDATE
        found.email = "ivan_updated@example.com"
        session.flush()
        print(f"✅ UPDATE: новый email → {found.email}")

        # DELETE
        session.delete(found)
        session.flush()
        print(f"✅ DELETE: пользователь id={user.id} удалён")

        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка: {e}")
    finally:
        session.close()


# ============================================================
#  Django ORM CRUD
# ============================================================
def django_crud():
    print("\n" + "=" * 60)
    print("🟢 Django ORM — CRUD операции")
    print("=" * 60)
    from models_django import DUser, DProduct, DOrder, DOrderItem

    # CREATE
    user = DUser.objects.create(
        name="Пётр Петров", email="petr_crud@example.com"
    )
    print(f"✅ CREATE: пользователь id={user.id}")

    product = DProduct.objects.create(name="Django товар", price=199.50)
    print(f"✅ CREATE: товар id={product.id}")

    order = DOrder.objects.create(user=user)
    DOrderItem.objects.create(order=order, product=product, quantity=3)
    print(f"✅ CREATE: заказ id={order.id} с позицией")

    # READ
    found = DUser.objects.get(id=user.id)
    print(f"✅ READ:   {found.name} / {found.email}")

    top3 = DUser.objects.order_by("name")[:3]
    print(f"✅ READ:   первые 3 — {[u.name for u in top3]}")

    # UPDATE
    found.email = "petr_updated@example.com"
    found.save()
    print(f"✅ UPDATE: новый email → {found.email}")

    # DELETE
    found.delete()
    print(f"✅ DELETE: пользователь id={user.id} удалён")


# ============================================================
#  Raw SQL CRUD  (pymssql)
# ============================================================
def raw_sql_crud():
    print("\n" + "=" * 60)
    print("🔴 Raw SQL (pymssql) — CRUD операции")
    print("=" * 60)
    conn = pymssql.connect(**MSSQL_CONFIG)
    cur  = conn.cursor()

    # CREATE — MS SQL: получаем id через OUTPUT
    cur.execute(
        "INSERT INTO users (name, email) OUTPUT INSERTED.id VALUES (%s, %s)",
        ("Сидор Сидоров", "sidor_crud@example.com")
    )
    uid = int(cur.fetchone()[0])
    print(f"✅ CREATE: пользователь id={uid}")

    cur.execute(
        "INSERT INTO products (name, price) OUTPUT INSERTED.id VALUES (%s, %s)",
        ("Raw товар", 299.00)
    )
    pid = int(cur.fetchone()[0])
    print(f"✅ CREATE: товар id={pid}")

    cur.execute(
        "INSERT INTO orders (user_id) OUTPUT INSERTED.id VALUES (%s)",
        (uid,)
    )
    oid = int(cur.fetchone()[0])
    cur.execute(
        "INSERT INTO order_items (order_id, product_id, quantity) "
        "VALUES (%s, %s, %s)", (oid, pid, 1)
    )
    print(f"✅ CREATE: заказ id={oid} с позицией")

    # READ
    cur.execute("SELECT name, email FROM users WHERE id = %s", (uid,))
    row = cur.fetchone()
    print(f"✅ READ:   {row[0]} / {row[1]}")

    cur.execute("SELECT TOP 3 name FROM users ORDER BY name")
    rows = cur.fetchall()
    print(f"✅ READ:   первые 3 — {[r[0] for r in rows]}")

    # UPDATE
    cur.execute("UPDATE users SET email = %s WHERE id = %s",
                ("sidor_updated@example.com", uid))
    print(f"✅ UPDATE: email обновлён")

    # DELETE (каскад удалит заказы и позиции)
    cur.execute("DELETE FROM users WHERE id = %s", (uid,))
    print(f"✅ DELETE: пользователь id={uid} удалён")

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    sqlalchemy_crud()
    django_crud()
    raw_sql_crud()
    print("\n" + "=" * 60)
    print("✅ Все CRUD-операции выполнены успешно!")
