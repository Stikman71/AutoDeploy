#!/bin/bash
PROJECT_DIR="$(pwd)"

# день недели (1=Пн, 7=Вс)
DAY_OF_WEEK=$(date +%u)

# db_init.py — только в воскресенье
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    python3 "$PROJECT_DIR/db_core/db_init.py"
fi

# generator.py — каждый день кроме воскресенья
if [ "$DAY_OF_WEEK" -ge 1 ] && [ "$DAY_OF_WEEK" -le 6 ]; then
    python3 "$PROJECT_DIR/generator.py"
fi


# load_data_db.py — каждый день
python3 "$PROJECT_DIR/load_data_db.py"
