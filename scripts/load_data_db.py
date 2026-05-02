import os
import re
import csv
import psycopg2
import configparser

# {{shop_num}}_{{cash_num}}.csv
FILENAME_PATTERN=re.compile(r"^\d+_\d+\.csv$")

# Загрузка данных для поключения к бд / где хранятся файлы data
def load_config(path="conf.ini"):
    config=configparser.ConfigParser()
    config.read(path)

    return {
        "db": {
            "host": config["db"]["host"],
            "port": int(config["db"]["port"]),
            "dbname": config["db"]["name"],
            "user": config["db"]["user"],
            "password": config["db"]["password"],
        },
        "data_dir": config["app"]["data_dir"]
    }


def is_valid_file(filename):
    """
    Соответсвие на название
    """
    return FILENAME_PATTERN.match(filename)


def parse_filename(filename):
    name=filename.replace(".csv", "")
    shop_num, cash_num=name.split("_")
    return int(shop_num), int(cash_num)


def process_file(cur, filepath, shop_num, cash_num):
    with open(filepath, encoding="utf-8") as f:
        reader=csv.DictReader(f)

        req_fields={"doc_id", "item", "category", "amount", "price", "discount"}
        
        if not req_fields.issubset(reader.fieldnames):
            print(f"SKIP {filepath} (not valid columns)")
            return

        for row in reader: # перенос файла в бд
            cur.execute("""
                INSERT INTO receipts (
                    doc_id, shop_num, cash_num,
                    item, category, amount, price, discount
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (doc_id, item, shop_num, cash_num)
                DO NOTHING
            """, (
                row["doc_id"],
                shop_num,
                cash_num,
                row["item"],
                row["category"],
                int(row["amount"]),
                float(row["price"]),
                float(row["discount"]),
            ))


def start():
    cfg=load_config()

    conn=psycopg2.connect(**cfg["db"]) # подкючение к бд
    cur=conn.cursor()

    data_dir=cfg["data_dir"] # дириктория с данными 


    for filename in os.listdir(data_dir): # обраотка фалов
        if not is_valid_file(filename):
            print(f"IGNORE {filename}")
            continue

        filepath=os.path.join(data_dir, filename) # Получание валидного файла

        try:
            shop_num, cash_num=parse_filename(filename)
            process_file(cur, filepath, shop_num, cash_num)
            conn.commit()
            print(f"LOAD {filename}")

        except Exception as e:
            conn.rollback()
            print(f"ERROR {filename}: {e}")

    cur.close()
    conn.close()


start()