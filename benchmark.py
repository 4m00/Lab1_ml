"""
Лабораторная работа №1, Часть 2.
Бенчмарк: SQLAlchemy ORM vs Django ORM vs Raw SQL (MS SQL Server)
6 типов запросов × 3 объёма данных (1k / 10k / 100k)
"""
import timeit
import json
import pymssql
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from models_sqlalchemy import get_engine, User, Product, Order, OrderItem
from db_config import MSSQL_CONFIG

engine  = get_engine()
Session = sessionmaker(bind=engine)

# Инициализация Django
from models_django import DUser, DProduct, DOrder, DOrderItem
from django.db.models import Count

REPEAT = 10


# ─────────────────────────────────────────
def measure(fn) -> float:
    return round(timeit.timeit(fn, number=REPEAT) / REPEAT, 6)

def raw_conn():
    return pymssql.connect(**MSSQL_CONFIG)

def first_user_id() -> int:
    conn = raw_conn()
    cur  = conn.cursor()
    cur.execute("SELECT TOP 1 id FROM users")
    uid  = cur.fetchone()[0]
    cur.close(); conn.close()
    return uid


# ─────────────────────────────────────────
# 1. SELECT по первичному ключу
# ─────────────────────────────────────────
def bench_select_by_id(uid):
    res = {}

    def sa():
        s = Session()
        s.query(User).filter(User.id == uid).first()
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        DUser.objects.filter(id=uid).first()
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (uid,))
        cur.fetchone(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# 2. Фильтрация + сортировка
# ─────────────────────────────────────────
def bench_filter_sort():
    res = {}

    def sa():
        s = Session()
        s.query(User).filter(User.name.like("А%")).order_by(User.name).limit(20).all()
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        list(DUser.objects.filter(name__startswith="А").order_by("name")[:20])
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.execute(
            "SELECT TOP 20 * FROM users WHERE name LIKE N'А%' ORDER BY name"
        )
        cur.fetchall(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# 3. JOIN
# ─────────────────────────────────────────
def bench_join():
    res = {}

    def sa():
        s = Session()
        (s.query(User, Order)
          .join(Order, User.id == Order.user_id)
          .limit(50).all())
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        list(DOrder.objects.select_related("user")[:50])
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.execute("""
            SELECT TOP 50 u.id, u.name, o.id, o.created_at
            FROM users u
            JOIN orders o ON u.id = o.user_id
        """)
        cur.fetchall(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# 4. Агрегат (COUNT, GROUP BY)
# ─────────────────────────────────────────
def bench_aggregate():
    res = {}

    def sa():
        s = Session()
        (s.query(User.id, func.count(Order.id).label("cnt"))
          .join(Order, User.id == Order.user_id)
          .group_by(User.id)
          .limit(50).all())
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        list(DUser.objects.annotate(cnt=Count("orders")).order_by("-cnt")[:50])
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.execute("""
            SELECT TOP 50 u.id, COUNT(o.id) AS cnt
            FROM users u
            LEFT JOIN orders o ON u.id = o.user_id
            GROUP BY u.id
            ORDER BY cnt DESC
        """)
        cur.fetchall(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# 5. Массовая вставка (bulk insert)
# ─────────────────────────────────────────
def bench_bulk_insert():
    res = {}
    N = 100

    def sa():
        s = Session()
        objs = [Product(name=f"bulk_{i}", price=10.0) for i in range(N)]
        s.bulk_save_objects(objs)
        s.commit()
        s.query(Product).filter(Product.name.like("bulk_%")).delete(
            synchronize_session=False)
        s.commit()
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        DProduct.objects.bulk_create(
            [DProduct(name=f"bulk_{i}", price=10.0) for i in range(N)]
        )
        DProduct.objects.filter(name__startswith="bulk_").delete()
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.executemany(
            "INSERT INTO products (name, price) VALUES (%s, %s)",
            [(f"bulk_{i}", 10.0) for i in range(N)]
        )
        c.commit()
        cur.execute("DELETE FROM products WHERE name LIKE 'bulk_%'")
        c.commit(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# 6. Массовое обновление (bulk update)
# ─────────────────────────────────────────
def bench_bulk_update():
    res = {}

    def sa():
        s = Session()
        s.query(Product).filter(Product.price < 100).update(
            {"price": Product.price * 1.1}, synchronize_session=False)
        s.commit()
        s.query(Product).filter(Product.price < 110).update(
            {"price": Product.price / 1.1}, synchronize_session=False)
        s.commit()
        s.close()
    res["SQLAlchemy ORM"] = measure(sa)

    def dj():
        from django.db.models import F
        DProduct.objects.filter(price__lt=100).update(price=F("price") * 1.1)
        DProduct.objects.filter(price__lt=110).update(price=F("price") / 1.1)
    res["Django ORM"] = measure(dj)

    def raw():
        c = raw_conn(); cur = c.cursor()
        cur.execute("UPDATE products SET price = price * 1.1 WHERE price < 100")
        c.commit()
        cur.execute("UPDATE products SET price = price / 1.1 WHERE price < 110")
        c.commit(); cur.close(); c.close()
    res["Raw SQL"] = measure(raw)

    return res


# ─────────────────────────────────────────
# Основная функция
# ─────────────────────────────────────────
QUERY_NAMES = [
    "SELECT по ID",
    "Фильтрация + сортировка",
    "JOIN",
    "Агрегат (GROUP BY)",
    "Массовая вставка",
    "Массовое обновление",
]
APPROACHES = ["SQLAlchemy ORM", "Django ORM", "Raw SQL"]


def run_benchmark(size: int) -> dict:
    print(f"\n{'='*65}")
    print(f"  БЕНЧМАРК — {size:,} записей  |  повторений: {REPEAT}")
    print(f"{'='*65}")
    uid = first_user_id()
    funcs = [
        lambda: bench_select_by_id(uid),
        bench_filter_sort,
        bench_join,
        bench_aggregate,
        bench_bulk_insert,
        bench_bulk_update,
    ]
    all_res = {}
    for name, fn in zip(QUERY_NAMES, funcs):
        print(f"  ⏳ {name}...", end=" ", flush=True)
        r = fn()
        all_res[name] = r
        print(f"SA={r['SQLAlchemy ORM']:.5f}  "
              f"DJ={r['Django ORM']:.5f}  "
              f"RAW={r['Raw SQL']:.5f}")
    return all_res


def print_table(data: dict):
    print(f"\n{'='*75}")
    print("  СВОДНАЯ ТАБЛИЦА (время в секундах)")
    print(f"{'='*75}")
    print(f"{'Запрос':<28} {'Объём':>7}  "
          + "".join(f"{a:>17}" for a in APPROACHES))
    print("-" * 75)
    for size, res in data.items():
        for qname, vals in res.items():
            row = f"{qname:<28} {size:>7}  "
            row += "".join(f"{vals[a]:>17.6f}" for a in APPROACHES)
            print(row)
        print("-" * 75)


if __name__ == "__main__":
    import generate_data
    all_data = {}
    for size in [1000, 10000, 100000]:
        print(f"\n🔄 Генерация данных: {size:,}...")
        generate_data.generate(size)
        all_data[size] = run_benchmark(size)

    print_table(all_data)

    with open("benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("\n💾 Результаты сохранены → benchmark_results.json")
