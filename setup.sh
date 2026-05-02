#!/bin/bash

set -e

PROJECT_DIR="$(pwd)"

echo "================================"
echo "Setting up project in: $PROJECT_DIR"
echo "================================"

# Проверка конфигурации
if [ ! -f "$PROJECT_DIR/conf.ini" ]; then
    echo "ERROR: config.ini not found!"
    echo "Check conf.ini."
    exit 1
fi

# Проверка python
if ! command -v python3 &> /dev/null
then
    echo "ERROR: python3 is not installed"
    exit 1
fi

# Очистка старых cron задач проекта
(crontab -l 2>/dev/null | grep -v "$PROJECT_DIR" || true) | crontab -

# Установка cron для daily_run.sh в 00:00 UTC
(crontab -l 2>/dev/null; echo "0 0 * * * TZ=UTC /bin/bash $PROJECT_DIR/daily_run.sh") | crontab -

echo "================================"
echo "SETUP COMPLETE"
echo "Cron installed"
echo "================================"


# 1. Инициализация БД
python3 "$PROJECT_DIR/db/db_init.py"

# 2. Генерация CSV
python3 "$PROJECT_DIR/scripts/generator.py"

# 3. Загрузка данных в БД
python3 "$PROJECT_DIR/scripts/load_data_db.py"
