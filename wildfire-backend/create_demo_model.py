#!/usr/bin/env python3
"""
Скрипт для создания демо ML модели
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.model_storage_service import ModelStorageService

def main():
    """Создать демо модель"""
    print("🤖 Создание демо ML модели...")
    
    try:
        storage = ModelStorageService()
        filename = storage.create_demo_model()
        
        if filename:
            print(f"✅ Демо модель создана: {filename}")
            
            # Показываем информацию о модели
            current_model = storage.get_current_model_info()
            if current_model:
                print(f"📊 Модель: {current_model['name']} v{current_model['version']}")
                print(f"📁 Файл: {current_model['filename']}")
                print(f"📏 Размер: {current_model['size_mb']} MB")
                print(f"📅 Создана: {current_model['created_at']}")
                
                if current_model['metrics']:
                    print("📈 Метрики:")
                    for metric, value in current_model['metrics'].items():
                        print(f"   {metric}: {value}")
                
                if current_model['features']:
                    print(f"🔧 Признаки ({len(current_model['features'])}):")
                    for feature in current_model['features']:
                        print(f"   - {feature}")
        else:
            print("❌ Ошибка создания демо модели")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main() 