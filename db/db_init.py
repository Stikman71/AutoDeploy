import psycopg2
import json
import configparser

# Конфигурация подключения к бд
config=configparser.ConfigParser()
config.read(r"conf.ini")

DB_CONFIG = {
    "host": config["db"]["host"],
    "port": config["db"]["port"],
    "dbname":   config["db"]["name"],
    "user": config["db"]["user"],
    "password": config["db"]["password"],
}

# Структура бд
SCHEMA_FILE=r"./db/db_schema.json"
def load_schema():
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def db_exists():
    """
    Проверка что базаданных существует по ее названию
    """
    conn=psycopg2.connect(
        dbname="postgres",
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    conn.autocommit=True
    cur=conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG["dbname"],))
    exists=cur.fetchone() is not None

    cur.close()
    conn.close()
    return exists


def create_db():
    """
    Первые запуск (если бд нет) создат новую
    """
    conn=psycopg2.connect(
        dbname="postgres",
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )
    conn.autocommit=True
    cur=conn.cursor()

    cur.execute(f"CREATE DATABASE {DB_CONFIG['dbname']}")

    cur.close()
    conn.close()


def create_tables(conn, schema):
    """
    Иницилизация таблицы по схеме
    Если таблица уже существует пропускает.
    """
    cur = conn.cursor()

    for table_name, table_data in schema["tables"].items():
        columns=table_data["columns"]
        constraints=table_data.get("constraints", [])

        cols_sql=", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        constr_sql=", ".join(constraints)

        full_sql=", ".join(filter(None, [cols_sql, constr_sql]))

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {full_sql}
            )
        """)

    conn.commit()
    cur.close()


def main():
    schema=load_schema()

    if not db_exists():
        create_db()

    conn=psycopg2.connect(**DB_CONFIG)

    create_tables(conn, schema)
    conn.close()

main()