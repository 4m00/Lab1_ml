# Лабораторная работа №1 — Инструкция (MS SQL Server)

## Структура файлов
```
lab1/
├── docker-compose.yml      # MS SQL Server в Docker
├── requirements.txt        # Python-зависимости
├── db_config.py            # Настройки подключения (один файл для всех)
├── create_tables.py        # Создание БД и таблиц
├── models_sqlalchemy.py    # Модели SQLAlchemy ORM
├── models_django.py        # Модели Django ORM
├── generate_data.py        # Генерация тестовых данных
├── crud_examples.py        # CRUD-операции (Часть 1)
├── benchmark.py            # Бенчмарк (Часть 2)
└── benchmark_graphics.py   # Графики (Часть 2)
```

---

## Шаг 1 — Установить Docker Desktop
Скачать: https://www.docker.com/products/docker-desktop/
После установки запустить Docker Desktop.

---

## Шаг 2 — Запустить MS SQL Server
```bash
docker compose up -d
```
Подождать 15–20 секунд пока сервер стартует.
Проверка: `docker ps` — должен быть контейнер `sqlserver-lab`

---

## Шаг 3 — Установка необходимых библиотек и зависимостей

### Windows:
```bash
pip install -r requirements.txt
```

> ⚠️ Для Django ORM дополнительно нужен ODBC Driver 17:
> - Windows: https://aka.ms/downloadmsodbcsql (скачать и установить)
> - macOS: `brew install msodbcsql17`
> - Ubuntu: `sudo apt install msodbcsql17`

---

## Шаг 4 — Создать таблицы
```bash
python create_tables.py
```

---

## Шаг 5 — Часть 1: CRUD
```bash
python generate_data.py 1000
python crud_examples.py
```

---

## Шаг 6 — Часть 2: Бенчмарк + графики
```bash
python benchmark.py            # занимает 10–20 минут
python benchmark_graphics.py   # создаёт PNG-файлы
```

---

## Пароль SA
По умолчанию: `Lab1Password!`
Изменить можно в `db_config.py` и `docker-compose.yml`
