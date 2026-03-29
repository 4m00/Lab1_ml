from sqlalchemy import (
    create_engine, Column, Integer, String,
    Numeric, ForeignKey, DateTime
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from db_config import SA_URL

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(255), nullable=False)
    email      = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    orders = relationship("Order", back_populates="user",
                          cascade="all, delete")

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"


class Product(Base):
    __tablename__ = "products"

    id    = Column(Integer, primary_key=True, autoincrement=True)
    name  = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user  = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order",
                         cascade="all, delete")

    def __repr__(self):
        return f"<Order(id={self.id}, user_id={self.user_id})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    order_id   = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"),
                        nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id})>"


def get_engine():
    return create_engine(SA_URL, echo=False)


if __name__ == "__main__":
    engine = get_engine()
    print("✅ SQLAlchemy подключён к MS SQL Server.")
    print(f"   URL: {SA_URL}")
    with engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        print(f"   Пользователей в БД: {result.scalar()}")
