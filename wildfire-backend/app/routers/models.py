from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict, Optional
from datetime import datetime
import json
from ..services.model_storage_service import ModelStorageService
from ..schemas.models import (
    ModelInfo, ModelList, ModelUpload, ModelMetrics
)

router = APIRouter(prefix="/api/v1/models", tags=["models"])

model_storage = ModelStorageService()

@router.get("/", response_model=ModelList)
async def get_models():
    """Получить список всех моделей"""
    try:
        models = model_storage.get_available_models()
        current_model = model_storage.get_current_model_info()
        
        return ModelList(
            models=models,
            current_model=current_model,
            total_count=len(models)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting models: {str(e)}")

@router.get("/current", response_model=Optional[ModelInfo])
async def get_current_model():
    """Получить информацию о текущей модели"""
    try:
        current_model = model_storage.get_current_model_info()
        if current_model:
            return ModelInfo(**current_model)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting current model: {str(e)}")

@router.post("/set-current/{model_filename}")
async def set_current_model(model_filename: str):
    """Установить модель как текущую"""
    try:
        success = model_storage.set_current_model(model_filename)
        if success:
            return {"message": f"Model {model_filename} set as current"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting current model: {str(e)}")

@router.delete("/{model_filename}")
async def delete_model(model_filename: str):
    """Удалить модель"""
    try:
        success = model_storage.delete_model(model_filename)
        if success:
            return {"message": f"Model {model_filename} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting model: {str(e)}")



@router.post("/upload")
async def upload_model(
    file: UploadFile = File(...),
    model_name: str = "wildfire_prediction",
    version: str = "1.0.0",
    metrics: Optional[str] = None,
    features: Optional[str] = None
):
    """Загрузить новую модель"""
    try:
        # Проверяем тип файла
        if not file.filename.endswith('.pkl'):
            raise HTTPException(status_code=400, detail="Only .pkl files are allowed")
        
        # Читаем файл
        content = await file.read()
        
        # Парсим метрики и признаки
        model_metrics = {}
        model_features = []
        
        if metrics:
            try:
                model_metrics = json.loads(metrics)
            except:
                model_metrics = {}
        
        if features:
            try:
                model_features = json.loads(features)
            except:
                model_features = []
        
        # Сохраняем модель во временный файл
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Загружаем модель для проверки
        try:
            import joblib
            model = joblib.load(tmp_file_path)
            
            # Сохраняем в хранилище
            filename = model_storage.save_model(
                model=model,
                model_name=model_name,
                version=version,
                metrics=model_metrics,
                features=model_features
            )
            
            # Удаляем временный файл
            import os
            os.unlink(tmp_file_path)
            
            return {
                "message": "Model uploaded successfully",
                "filename": filename,
                "model_name": model_name,
                "version": version
            }
            
        except Exception as e:
            # Удаляем временный файл в случае ошибки
            import os
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
            raise HTTPException(status_code=400, detail=f"Invalid model file: {str(e)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading model: {str(e)}") 