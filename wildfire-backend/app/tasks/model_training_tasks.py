"""
Celery tasks for model training.
"""
from celery import current_task
from typing import Dict, Any, List
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import lightgbm as lgb

from ..core.celery_app import celery_app
from ..services.database_service import DatabaseService
from ..services.mlflow_service import MLflowService
from ..services.minio_service import MinIOService

logger = logging.getLogger(__name__)

db_service = DatabaseService()
mlflow_service = MLflowService()
minio_service = MinIOService()

@celery_app.task(bind=True)
def train_model_task(self, training_config: Dict[str, Any]) -> Dict[str, Any]:
    """Обучение модели"""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Preparing training data..."}
        )
        
        # Получаем данные для обучения
        training_data = prepare_training_data(training_config)
        
        if not training_data or len(training_data) == 0:
            return {
                "status": "failed",
                "error": "No training data available"
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Splitting data..."}
        )
        
        # Разделяем данные на train/test
        X = training_data.drop('fire_occurred', axis=1)
        y = training_data['fire_occurred']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 40, "total": 100, "status": "Training model..."}
        )
        
        # Обучаем модель
        model = train_lightgbm_model(X_train, y_train, training_config)
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 70, "total": 100, "status": "Evaluating model..."}
        )
        
        # Оцениваем модель
        y_pred = model.predict(X_test)
        metrics = calculate_metrics(y_test, y_pred)
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Saving model..."}
        )
        
        # Сохраняем модель в MLflow
        model_version = save_model_to_mlflow(model, metrics, training_config)
        
        return {
            "status": "completed",
            "model_version": model_version,
            "metrics": metrics,
            "training_samples": len(training_data),
            "test_samples": len(X_test)
        }
        
    except Exception as e:
        logger.error(f"Error in model training task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

@celery_app.task(bind=True)
def evaluate_model_task(self, model_version: str) -> Dict[str, Any]:
    """Оценка модели"""
    try:
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "Loading model..."}
        )
        
        # Загружаем модель
        model = mlflow_service.get_latest_model()
        
        if not model:
            return {
                "status": "failed",
                "error": "Model not found"
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 30, "total": 100, "status": "Preparing evaluation data..."}
        )
        
        # Получаем тестовые данные
        test_data = prepare_evaluation_data()
        
        if not test_data or len(test_data) == 0:
            return {
                "status": "failed",
                "error": "No evaluation data available"
            }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Evaluating model..."}
        )
        
        # Оцениваем модель
        X_test = test_data.drop('fire_occurred', axis=1)
        y_test = test_data['fire_occurred']
        
        y_pred = model.predict(X_test)
        metrics = calculate_metrics(y_test, y_pred)
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 90, "total": 100, "status": "Saving results..."}
        )
        
        # Сохраняем результаты оценки
        evaluation_result = {
            "model_version": model_version,
            "evaluation_date": datetime.now().isoformat(),
            "metrics": metrics,
            "test_samples": len(test_data)
        }
        
        minio_service.upload_json(f"evaluations/{model_version}_evaluation.json", evaluation_result)
        
        return {
            "status": "completed",
            "model_version": model_version,
            "metrics": metrics,
            "test_samples": len(test_data)
        }
        
    except Exception as e:
        logger.error(f"Error in model evaluation task: {e}")
        return {
            "status": "failed",
            "error": str(e)
        }

def prepare_training_data(config: Dict[str, Any]) -> pd.DataFrame:
    """Подготовка данных для обучения"""
    # TODO: Получить данные из БД
    # Пока создаем синтетические данные
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'latitude': np.random.uniform(50, 80, n_samples),
        'longitude': np.random.uniform(30, 180, n_samples),
        'temperature': np.random.uniform(-30, 35, n_samples),
        'humidity': np.random.uniform(20, 100, n_samples),
        'wind_u': np.random.uniform(-20, 20, n_samples),
        'wind_v': np.random.uniform(-20, 20, n_samples),
        'precipitation': np.random.uniform(0, 50, n_samples),
        'year': np.random.randint(2020, 2024, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'weekday': np.random.randint(0, 7, n_samples),
    }
    
    # Создаем целевую переменную (пожар произошел или нет)
    # Простая логика: высокий риск при высокой температуре и низкой влажности
    fire_risk = (
        (data['temperature'] > 25) & 
        (data['humidity'] < 40) & 
        (data['precipitation'] < 5)
    ).astype(int)
    
    data['fire_occurred'] = fire_risk
    
    return pd.DataFrame(data)

def prepare_evaluation_data() -> pd.DataFrame:
    """Подготовка данных для оценки"""
    # Аналогично prepare_training_data, но с другими данными
    return prepare_training_data({})

def train_lightgbm_model(X_train: pd.DataFrame, y_train: pd.Series, config: Dict[str, Any]) -> lgb.LGBMClassifier:
    """Обучение LightGBM модели"""
    model_params = config.get("model_params", {
        "objective": "binary",
        "metric": "binary_logloss",
        "boosting_type": "gbdt",
        "num_leaves": 31,
        "learning_rate": 0.05,
        "feature_fraction": 0.9,
        "bagging_fraction": 0.8,
        "bagging_freq": 5,
        "verbose": -1
    })
    
    model = lgb.LGBMClassifier(**model_params)
    model.fit(X_train, y_train)
    
    return model

def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray) -> Dict[str, float]:
    """Расчет метрик модели"""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1_score": f1_score(y_true, y_pred)
    }

def save_model_to_mlflow(model: lgb.LGBMClassifier, metrics: Dict[str, float], config: Dict[str, Any]) -> str:
    """Сохранение модели в MLflow"""
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("wildfire-prediction")
    
    with mlflow.start_run():
        # Логируем параметры
        mlflow.log_params(config.get("model_params", {}))
        
        # Логируем метрики
        mlflow.log_metrics(metrics)
        
        # Сохраняем модель
        mlflow.sklearn.log_model(model, "model")
        
        # Получаем run_id
        run_id = mlflow.active_run().info.run_id
        
        # Регистрируем модель
        model_uri = f"runs:/{run_id}/model"
        model_version = mlflow.register_model(model_uri, "wildfire-prediction")
        
        return model_version.version 