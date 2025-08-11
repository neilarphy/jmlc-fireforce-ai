#!/usr/bin/env python3
"""
Скрипт для регистрации существующих моделей в системе
"""
import os
import json
from pathlib import Path
from datetime import datetime
import joblib

def register_existing_models():
    """Регистрировать существующие модели в метаданных"""
    
    models_dir = Path("models")
    metadata_file = models_dir / "metadata.json"
    
    # Создаем базовую структуру метаданных
    metadata = {
        "models": {},
        "current_model": None,
        "last_updated": datetime.now().isoformat()
    }
    
    # Ищем все .pkl файлы в папке models
    model_files = list(models_dir.glob("*.pkl"))
    
    if not model_files:
        print("No model files found in models/ directory")
        return
    
    print(f"Found {len(model_files)} model files:")
    
    for model_file in model_files:
        try:
            # Пытаемся загрузить модель для проверки
            model = joblib.load(model_file)
            
            # Получаем информацию о модели
            file_size = model_file.stat().st_size / (1024 * 1024)  # MB
            created_time = datetime.fromtimestamp(model_file.stat().st_mtime)
            
            # Определяем тип модели
            model_type = type(model).__name__
            
            # Создаем информацию о модели
            model_info = {
                "name": "wildfire_model",
                "version": "1.0",
                "filename": model_file.name,
                "path": str(model_file.absolute()),
                "created_at": created_time.isoformat(),
                "model_type": model_type,
                "size_mb": round(file_size, 2),
                "features": [],  # Будет заполнено позже
                "metrics": {}    # Будет заполнено позже
            }
            
            metadata["models"][model_file.name] = model_info
            print(f"  ✓ {model_file.name} ({model_type}, {file_size:.1f}MB)")
            
        except Exception as e:
            print(f"  ✗ {model_file.name} - Error: {e}")
    
    # Устанавливаем самую новую модель как текущую
    if metadata["models"]:
        latest_model = max(metadata["models"].values(), 
                          key=lambda x: x["created_at"])
        metadata["current_model"] = latest_model["filename"]
        print(f"\nSet current model to: {latest_model['filename']}")
    
    # Сохраняем метаданные
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\nMetadata saved to: {metadata_file}")
    print(f"Registered {len(metadata['models'])} models")

if __name__ == "__main__":
    register_existing_models() 