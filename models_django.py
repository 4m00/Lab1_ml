"""
Django ORM модели — standalone, без полного Django-проекта.
Бэкенд: mssql-django (pip install mssql-django)
Запуск: python models_django.py
"""
import django
from django.conf import settings
from db_config import DJANGO_DB

if not settings.configured:
    settings.configure(
        DATABASES={"default": DJANGO_DB},
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        USE_TZ=False,
    )
    django.setup()

from django.db import models


class DUser(models.Model):
    name       = models.CharField(max_length=255)
    email      = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "auth"
        db_table  = "users"
        managed   = False   # таблица уже создана create_tables.py

    def __str__(self):
        return f"User({self.id}, {self.name})"


class DProduct(models.Model):
    name  = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        app_label = "auth"
        db_table  = "products"
        managed   = False

    def __str__(self):
        return f"Product({self.id}, {self.name})"


class DOrder(models.Model):
    user       = models.ForeignKey(
        DUser, on_delete=models.CASCADE,
        db_column="user_id", related_name="orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "auth"
        db_table  = "orders"
        managed   = False

    def __str__(self):
        return f"Order({self.id}, user_id={self.user_id})"


class DOrderItem(models.Model):
    order   = models.ForeignKey(
        DOrder, on_delete=models.CASCADE,
        db_column="order_id", related_name="items"
    )
    product = models.ForeignKey(
        DProduct, on_delete=models.PROTECT,
        db_column="product_id"
    )
    quantity = models.IntegerField()

    class Meta:
        app_label = "auth"
        db_table  = "order_items"
        managed   = False

    def __str__(self):
        return f"OrderItem(order={self.order_id}, product={self.product_id})"


if __name__ == "__main__":
    count = DUser.objects.count()
    print("✅ Django ORM подключён к MS SQL Server.")
    print(f"   Пользователей в БД: {count}")
    print("   Модели: DUser, DProduct, DOrder, DOrderItem")
