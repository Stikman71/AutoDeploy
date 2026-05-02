import csv
import os
import random
import string
import configparser

config=configparser.ConfigParser()
config.read(r"conf.ini")

# Папка для выгрузок
output_dir=config["app"]["data_dir"]
os.makedirs(output_dir, exist_ok=True)

# Настройки генерации
NUM_SHOPS=5 # количество магазинов
MAX_CASH_REGISTERS=3    # максимум касс в магазине
MAX_CHECKS_PER_CASH=10    # максимум чеков на кассу
MAX_ITEMS_PER_CHECK=5 # максимум товаров в чеке

# Тестовый список (товаров, категорий)
items = [
    ("Стиральный порошок", "Бытовая химия"),
    ("Тарелка", "Посуда"),
    ("Полотенце", "Текстиль"),
    ("Мыло", "Бытовая химия"),
    ("Сковорода", "Посуда"),
    ("Футболка", "Текстиль"),
]

# Генерация случайного doc_id
def generate_doc_id(length=6):
    return ''.join(random.choices(string.ascii_letters+string.digits, k=length))

# Генерация данных для одного чека
def generate_check():
    num_items=random.randint(1, MAX_ITEMS_PER_CHECK)
    check_rows=[]
    dock_id=generate_doc_id()
    for _ in range(num_items):
        item_name, category=random.choice(items)
        amount=random.randint(1, 5)
        price=round(random.uniform(50, 1000), 2)
        discount=round(random.choice([0, random.uniform(5, 100)]), 2)
        check_rows.append({
            "doc_id": dock_id,
            "item": item_name,
            "category": category,
            "amount": amount,
            "price": price,
            "discount": discount
        })
    return check_rows

# Генерация CSV для всех магазинов и касс
for shop_num in range(1, NUM_SHOPS+1):
    num_cash_registers=random.randint(1, MAX_CASH_REGISTERS)
    for cash_num in range(1, num_cash_registers+1):
        filename=f"{shop_num}_{cash_num}.csv"
        filepath=os.path.join(output_dir, filename)
        
        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            fieldnames=["doc_id", "item", "category", "amount", "price", "discount"]
            writer=csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            num_checks=random.randint(1, MAX_CHECKS_PER_CASH)
            for _ in range(num_checks):
                check=generate_check()
                for row in check:
                    writer.writerow(row)

print(f"Сгенерировано CSV-файлов для {NUM_SHOPS} магазинов в папке '{output_dir}'")