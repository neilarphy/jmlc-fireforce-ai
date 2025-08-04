#!/usr/bin/env python3
"""
Скрипт для управления миграциями базы данных.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str) -> bool:
    """Выполнение команды"""
    print(f"🔄 Выполняю: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Успешно: {command}")
        if result.stdout:
            print(result.stdout)
        return True
    else:
        print(f"❌ Ошибка: {command}")
        if result.stderr:
            print(result.stderr)
        return False

def init_alembic():
    """Инициализация Alembic"""
    print("🚀 Инициализация Alembic...")
    return run_command("alembic init alembic")

def create_migration(message: str):
    """Создание новой миграции"""
    print(f"📝 Создание миграции: {message}")
    return run_command(f'alembic revision --autogenerate -m "{message}"')

def upgrade_database():
    """Применение миграций"""
    print("⬆️ Применение миграций...")
    return run_command("alembic upgrade head")

def downgrade_database(revision: str = "-1"):
    """Откат миграций"""
    print(f"⬇️ Откат миграций до {revision}...")
    return run_command(f"alembic downgrade {revision}")

def show_migrations():
    """Показать историю миграций"""
    print("📋 История миграций:")
    return run_command("alembic history")

def show_current():
    """Показать текущую версию"""
    print("📍 Текущая версия:")
    return run_command("alembic current")

def create_initial_migration():
    """Создание начальной миграции"""
    print("🏗️ Создание начальной миграции...")
    
    # Создаем миграцию со всеми таблицами
    success = create_migration("Initial migration - create all tables")
    
    if success:
        print("✅ Начальная миграция создана")
        print("💡 Теперь выполните: python migrate.py upgrade")
    else:
        print("❌ Ошибка создания миграции")
    
    return success

def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("""
🔥 Wildfire Prediction - Управление миграциями

Использование:
  python migrate.py <команда> [параметры]

Команды:
  init          - Инициализация Alembic
  create        - Создание новой миграции
  upgrade       - Применение миграций
  downgrade     - Откат миграций
  history       - История миграций
  current       - Текущая версия
  initial       - Создание начальной миграции

Примеры:
  python migrate.py init
  python migrate.py create "Add user table"
  python migrate.py upgrade
  python migrate.py initial
        """)
        return
    
    command = sys.argv[1]
    
    if command == "init":
        init_alembic()
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Укажите сообщение для миграции")
            return
        create_migration(sys.argv[2])
    elif command == "upgrade":
        upgrade_database()
    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        downgrade_database(revision)
    elif command == "history":
        show_migrations()
    elif command == "current":
        show_current()
    elif command == "initial":
        create_initial_migration()
    else:
        print(f"❌ Неизвестная команда: {command}")

if __name__ == "__main__":
    main() 