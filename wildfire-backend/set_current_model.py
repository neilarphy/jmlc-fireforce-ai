#!/usr/bin/env python3
"""
Скрипт для установки текущей модели
"""
import shutil
from pathlib import Path
import json

def set_current_model():
    """Установить текущую модель"""
    
    models_dir = Path("models")
    metadata_file = models_dir / "metadata.json"
    current_model_path = models_dir / "current_model.pkl"
    
    # Загружаем метаданные
    if not metadata_file.exists():
        print("Metadata file not found. Run register_models.py first.")
        return
    
    with open(metadata_file, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    current_model_name = metadata.get("current_model")
    if not current_model_name:
        print("No current model set in metadata.")
        return
    
    if current_model_name not in metadata["models"]:
        print(f"Current model {current_model_name} not found in metadata.")
        return
    
    model_info = metadata["models"][current_model_name]
    source_path = Path(model_info["path"])
    
    if not source_path.exists():
        print(f"Model file not found: {source_path}")
        return
    
    # Копируем модель как текущую
    shutil.copy2(source_path, current_model_path)
    
    print(f"Current model set to: {current_model_name}")
    print(f"Copied from: {source_path}")
    print(f"Copied to: {current_model_path}")
    print(f"Model type: {model_info['model_type']}")
    print(f"Size: {model_info['size_mb']}MB")

if __name__ == "__main__":
    set_current_model() 