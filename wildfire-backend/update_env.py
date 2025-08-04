#!/usr/bin/env python3
"""
Скрипт для обновления .env файла с новой схемой fireforceai
"""

def update_env():
    with open('.env', 'r') as f:
        content = f.read()
    
    # Обновляем DATABASE_URL с новой схемой
    old_url = "92.51.23.44:5433/wildfire"
    new_url = "92.51.23.44:5433/wildfire?options=-csearch_path%3Dfireforceai"
    
    content = content.replace(old_url, new_url)
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Схема fireforceai добавлена в DATABASE_URL!")

if __name__ == "__main__":
    update_env() 