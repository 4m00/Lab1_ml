# Общие настройки подключения к MS SQL Server
# Используется во всех скриптах

MSSQL_CONFIG = {
    "server":   "localhost",
    "port":     1433,
    "user":     "sa",
    "password": "Lab1Password!",
    "database": "orm_test",
}

# SQLAlchemy URL (через pymssql)
SA_URL = (
    "mssql+pymssql://sa:Lab1Password!@localhost:1433/orm_test"
    "?charset=utf8"
)

# Django DATABASE settings
DJANGO_DB = {
    "ENGINE":   "mssql",
    "NAME":     "orm_test",
    "USER":     "sa",
    "PASSWORD": "Lab1Password!",
    "HOST":     "127.0.0.1,1433",
    "OPTIONS":  {
        "driver": "ODBC Driver 18 for SQL Server",
        "extra_params": "TrustServerCertificate=yes;Encrypt=no;Connection Timeout=30;Login Timeout=30",
    },
}
