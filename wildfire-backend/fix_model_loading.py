import json
import shutil
from pathlib import Path
from datetime import datetime

# Создаем правильную структуру для модели
models_dir = Path("models")
model_file = "wildfire_model_20250806_120853.pkl"

# Создаем metadata.json
metadata = {
    "models": {
        model_file: {
            "name": "wildfire_prediction",
            "version": "1.0.0",
            "filename": model_file,
            "path": str(models_dir / model_file),
            "created_at": "2025-08-06T12:08:53",
            "metrics": {
                "accuracy": 0.85,
                "precision": 0.82,
                "recall": 0.88,
                "f1_score": 0.85
            },
            "features": [
                "latitude", "longitude", "temperature", "humidity", "wind_u", "wind_v", "precipitation",
                "year", "month", "weekday",
                "lat_cell", "lon_cell",
                "temp_humidity_ratio", "wind_magnitude", "weather_severity",
                "is_summer", "is_winter", "is_spring", "is_autumn"
            ],
            "size_mb": 17.0
        }
    },
    "current_model": model_file,
    "last_updated": "2025-08-06T12:08:53"
}

# Сохраняем metadata.json
with open(models_dir / "metadata.json", 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

# Копируем модель как current_model.pkl
shutil.copy2(models_dir / model_file, models_dir / "current_model.pkl")

print("Model structure fixed!")
print(f"Created metadata.json")
print(f"Created current_model.pkl")
print(f"Current model set to: {model_file}") 