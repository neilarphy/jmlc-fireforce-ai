"""
Сервис для управления хранением ML моделей
"""
import os
import joblib
import logging
from typing import Optional, Dict, List
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelStorageService:
    """Сервис для управления ML моделями"""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.model_metadata_file = self.models_dir / "metadata.json"
        self.current_model_path = self.models_dir / "current_model.pkl"
        self.model_metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Загрузить метаданные моделей"""
        if self.model_metadata_file.exists():
            try:
                with open(self.model_metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading model metadata: {e}")
        return {
            "models": {},
            "current_model": None,
            "last_updated": None
        }
    
    def _save_metadata(self):
        """Сохранить метаданные моделей"""
        try:
            with open(self.model_metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving model metadata: {e}")
    
    def save_model(self, model, model_name: str, version: str, 
                   metrics: Dict = None, features: List[str] = None) -> str:
        """Сохранить модель"""
        try:
            # Создаем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_name}_v{version}_{timestamp}.pkl"
            model_path = self.models_dir / filename
            
            # Сохраняем модель
            joblib.dump(model, model_path)
            
            # Обновляем метаданные
            model_info = {
                "name": model_name,
                "version": version,
                "filename": filename,
                "path": str(model_path),
                "created_at": datetime.now().isoformat(),
                "metrics": metrics or {},
                "features": features or [],
                "size_mb": round(model_path.stat().st_size / (1024 * 1024), 2)
            }
            
            self.model_metadata["models"][filename] = model_info
            self.model_metadata["last_updated"] = datetime.now().isoformat()
            self._save_metadata()
            
            logger.info(f"Model saved: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise
    
    def load_model(self, model_path: Optional[str] = None) -> Optional[object]:
        """Загрузить модель"""
        try:
            if model_path is None:
                # Загружаем текущую модель
                if self.current_model_path.exists():
                    model_path = str(self.current_model_path)
                else:
                    # Ищем последнюю модель
                    models = self.get_available_models()
                    if not models:
                        logger.warning("No models available")
                        return None
                    latest_model = max(models, key=lambda x: x["created_at"])
                    model_path = latest_model["path"]
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return None
            
            model = joblib.load(model_path)
            logger.info(f"Model loaded: {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def set_current_model(self, model_filename: str) -> bool:
        """Установить модель как текущую"""
        try:
            if model_filename not in self.model_metadata["models"]:
                logger.error(f"Model not found in metadata: {model_filename}")
                return False
            
            model_info = self.model_metadata["models"][model_filename]
            source_path = Path(model_info["path"])
            
            if not source_path.exists():
                logger.error(f"Model file not found: {source_path}")
                return False
            
            # Копируем модель как текущую
            import shutil
            shutil.copy2(source_path, self.current_model_path)
            
            self.model_metadata["current_model"] = model_filename
            self._save_metadata()
            
            logger.info(f"Current model set to: {model_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting current model: {e}")
            return False
    
    def get_available_models(self) -> List[Dict]:
        """Получить список доступных моделей"""
        models = []
        for filename, info in self.model_metadata["models"].items():
            if Path(info["path"]).exists():
                models.append(info)
        return sorted(models, key=lambda x: x["created_at"], reverse=True)
    
    def get_current_model_info(self) -> Optional[Dict]:
        """Получить информацию о текущей модели"""
        current_model = self.model_metadata.get("current_model")
        if current_model and current_model in self.model_metadata["models"]:
            return self.model_metadata["models"][current_model]
        return None
    
    def delete_model(self, model_filename: str) -> bool:
        """Удалить модель"""
        try:
            if model_filename not in self.model_metadata["models"]:
                logger.error(f"Model not found: {model_filename}")
                return False
            
            model_info = self.model_metadata["models"][model_filename]
            model_path = Path(model_info["path"])
            
            if model_path.exists():
                model_path.unlink()
            
            del self.model_metadata["models"][model_filename]
            
            # Если удаляем текущую модель, сбрасываем указатель
            if self.model_metadata.get("current_model") == model_filename:
                self.model_metadata["current_model"] = None
                if self.current_model_path.exists():
                    self.current_model_path.unlink()
            
            self._save_metadata()
            logger.info(f"Model deleted: {model_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return False
    
 