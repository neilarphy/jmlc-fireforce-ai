import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.model_storage_service import ModelStorageService

# Тестируем ModelStorageService
storage = ModelStorageService()

print("Testing ModelStorageService...")

# Проверяем доступные модели
models = storage.get_available_models()
print(f"Available models: {len(models)}")
for model in models:
    print(f"  - {model['filename']} (created: {model['created_at']})")

# Проверяем текущую модель
current_model = storage.get_current_model_info()
if current_model:
    print(f"Current model: {current_model['filename']}")
else:
    print("No current model set")

# Загружаем модель
model = storage.load_model()
if model is not None:
    print("Model loaded successfully!")
    print(f"Model type: {type(model)}")
    print(f"Model has predict_proba: {hasattr(model, 'predict_proba')}")
    
    # Тестируем предсказание
    import numpy as np
    test_features = np.random.rand(1, 19)
    prediction = model.predict_proba(test_features)
    print(f"Test prediction: {prediction}")
else:
    print("Failed to load model") 