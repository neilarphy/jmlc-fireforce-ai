"""
DAG для обучения LightGBM модели предсказания пожаров
Использует данные из training_features с погодными данными
Интегрирован с MLflow для трекинга экспериментов
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
import pandas as pd
import numpy as np
import optuna
import joblib
import json
import logging
from sklearn.model_selection import train_test_split
import lightgbm as lgb
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
from sklearn.preprocessing import StandardScaler
import tempfile
import os
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient

# Настройка логирования
logger = logging.getLogger(__name__)

# Параметры DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 8, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'wildfire_ml_training',
    default_args=default_args,
    description='ML Training Pipeline for Wildfire Prediction with MLflow',
    schedule_interval=None,
    catchup=False,
    tags=['wildfire', 'ml', 'training', 'mlflow']
)

# ============================================================================
# TASK 1: Проверка данных и подготовка выборки
# ============================================================================

def prepare_training_data(**context):
    """
    Подготовка данных для обучения модели.
    Выбирает сбалансированную выборку с заполненными погодными данными.
    """
    logger.info("Starting training data preparation")
    
    pg_hook = PostgresHook(postgres_conn_id='wildfire_db')
    
    # Проверяем доступность данных
    check_sql = """
    SELECT 
        COUNT(*) as total_samples,
        COUNT(*) FILTER (WHERE fire_occurred = true) as positive_samples,
        COUNT(*) FILTER (WHERE fire_occurred = false) as negative_samples,
        COUNT(*) FILTER (WHERE temperature IS NOT NULL AND humidity IS NOT NULL AND wind_u IS NOT NULL AND precipitation IS NOT NULL) as samples_with_weather,
        COUNT(*) FILTER (WHERE fire_occurred = true AND temperature IS NOT NULL AND humidity IS NOT NULL AND wind_u IS NOT NULL AND precipitation IS NOT NULL) as positive_with_weather,
        COUNT(*) FILTER (WHERE fire_occurred = false AND temperature IS NOT NULL AND humidity IS NOT NULL AND wind_u IS NOT NULL AND precipitation IS NOT NULL) as negative_with_weather
    FROM fireforceai.training_features
    """
    
    result = pg_hook.get_first(check_sql)
    if not result:
        raise Exception("No data found in training_features table")
    
    total_samples, positive_samples, negative_samples, samples_with_weather, positive_with_weather, negative_with_weather = result
    
    logger.info(f"Data availability: Total={total_samples}, Positive={positive_samples}, Negative={negative_samples}")
    logger.info(f"Weather data: Total with weather={samples_with_weather}, Positive with weather={positive_with_weather}, Negative with weather={negative_with_weather}")
    
    # Определяем размер выборки (балансируем позитивы и негативы)
    sample_size = min(positive_with_weather, negative_with_weather, 10000)  # Максимум 10k каждого класса
    
    if sample_size < 1000:
        raise Exception(f"Not enough data for training. Need at least 1000 samples per class, got {sample_size}")
    
    logger.info(f"Using balanced sample size: {sample_size} per class (total: {sample_size * 2})")
    
    # Загружаем сбалансированную выборку
    data_sql = f"""
    (
        SELECT * FROM fireforceai.training_features 
        WHERE fire_occurred = true 
        AND temperature IS NOT NULL 
        AND humidity IS NOT NULL 
        AND wind_u IS NOT NULL 
        AND precipitation IS NOT NULL
        ORDER BY RANDOM()
        LIMIT {sample_size}
    )
    UNION ALL
    (
        SELECT * FROM fireforceai.training_features 
        WHERE fire_occurred = false 
        AND temperature IS NOT NULL 
        AND humidity IS NOT NULL 
        AND wind_u IS NOT NULL 
        AND precipitation IS NOT NULL
        ORDER BY RANDOM()
        LIMIT {sample_size}
    )
    """
    
    df = pd.read_sql(data_sql, pg_hook.get_conn())
    
    logger.info(f"Loaded {len(df)} samples: {df['fire_occurred'].sum()} positive, {(~df['fire_occurred']).sum()} negative")
    
    # Feature engineering
    logger.info("Performing feature engineering...")
    
    # КОНВЕРТАЦИЯ ТЕМПЕРАТУР ИЗ КЕЛЬВИНОВ В ЦЕЛЬСИИ
    # ERA5 возвращает температуры в Кельвинах, нужно конвертировать в Цельсии
    logger.info("Converting temperatures from Kelvin to Celsius...")
    
    # Проверяем диапазон температур для определения единиц измерения
    temp_min = df['temperature'].min()
    temp_max = df['temperature'].max()
    logger.info(f"Temperature range before conversion: {temp_min:.2f} to {temp_max:.2f}")
    
    # Если температуры в Кельвинах (обычно 250-320K), конвертируем в Цельсии
    if temp_min > 200 and temp_max < 350:  # Диапазон Кельвинов
        logger.info("Detected Kelvin temperatures, converting to Celsius...")
        df['temperature'] = df['temperature'] - 273.15
        logger.info(f"Temperature range after conversion: {df['temperature'].min():.2f}°C to {df['temperature'].max():.2f}°C")
    else:
        logger.info("Temperatures already in Celsius, no conversion needed")
    
    # Временные признаки
    df['year'] = pd.to_datetime(df['dt']).dt.year
    df['month'] = pd.to_datetime(df['dt']).dt.month
    df['day_of_year'] = pd.to_datetime(df['dt']).dt.dayofyear
    df['weekday'] = pd.to_datetime(df['dt']).dt.weekday
    
    # Географические признаки
    df['lat_rounded'] = np.round(df['latitude'], 1)
    df['lon_rounded'] = np.round(df['longitude'], 1)
    
    # Выбираем фичи для модели (соответствуют схеме таблицы)
    feature_columns = [
        'latitude', 'longitude', 'temperature', 'humidity', 'wind_u', 'wind_v', 'precipitation',
        'year', 'month', 'weekday',
        'lat_cell', 'lon_cell'
    ]
    
    # Добавляем вычисляемые признаки
    df['temp_humidity_ratio'] = df['temperature'] / (df['humidity'] + 1e-6)
    df['wind_magnitude'] = np.sqrt(df['wind_u']**2 + df['wind_v']**2)
    df['weather_severity'] = df['temperature'] * df['wind_magnitude'] / (df['humidity'] + 1e-6)
    df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
    df['is_winter'] = df['month'].isin([12, 1, 2]).astype(int)
    df['is_spring'] = df['month'].isin([3, 4, 5]).astype(int)
    df['is_autumn'] = df['month'].isin([9, 10, 11]).astype(int)
    
    # Финальный список признаков
    final_feature_columns = feature_columns + [
        'temp_humidity_ratio', 'wind_magnitude', 'weather_severity',
        'is_summer', 'is_winter', 'is_spring', 'is_autumn'
    ]
    
    X = df[final_feature_columns]
    y = df['fire_occurred'].astype(int)
    
    # Разделяем на train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Сохраняем данные в XCom
    training_data = {
        'X_train': X_train.to_dict(),
        'X_test': X_test.to_dict(),
        'y_train': y_train.to_dict(),
        'y_test': y_test.to_dict(),
        'feature_columns': final_feature_columns,
        'sample_size': sample_size,
        'total_samples': len(df),
        'positive_samples': y.sum(),
        'negative_samples': len(y) - y.sum()
    }
    
    context['task_instance'].xcom_push(key='training_data', value=training_data)
    
    logger.info(f"Training data prepared: {len(X_train)} train samples, {len(X_test)} test samples")
    logger.info(f"Features: {len(final_feature_columns)} columns")
    
    return f"Prepared {len(df)} samples with {len(final_feature_columns)} features"

prepare_data = PythonOperator(
    task_id='prepare_training_data',
    python_callable=prepare_training_data,
    dag=dag
)

# ============================================================================
# TASK 2: Оптимизация гиперпараметров с Optuna
# ============================================================================

def optimize_hyperparameters(**context):
    """
    Оптимизация гиперпараметров модели с помощью Optuna и MLflow.
    """
    logger.info("Starting hyperparameter optimization with Optuna and MLflow")
    
    # Получаем данные из предыдущего таска
    training_data = context['task_instance'].xcom_pull(key='training_data', task_ids='prepare_training_data')
    
    X_train = pd.DataFrame.from_dict(training_data['X_train'])
    X_test = pd.DataFrame.from_dict(training_data['X_test'])
    y_train = pd.Series(training_data['y_train'])
    y_test = pd.Series(training_data['y_test'])
    feature_columns = training_data['feature_columns']
    
    # Скалируем данные
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Настройка MLflow
    mlflow.set_tracking_uri("http://92.51.23.44:5000")
    experiment_name = "wildfire_prediction"
    
    # Создаем или получаем эксперимент
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id
    
    logger.info(f"Using MLflow experiment: {experiment_name} (ID: {experiment_id})")
    
    def objective(trial):
        """Objective function for Optuna optimization with MLflow logging"""
        
        # Гиперпараметры для LightGBM
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 16, 256),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'min_data_in_leaf': trial.suggest_int('min_data_in_leaf', 10, 100),
            'feature_fraction': trial.suggest_float('feature_fraction', 0.5, 1.0),
            'bagging_fraction': trial.suggest_float('bagging_fraction', 0.5, 1.0),
            'bagging_freq': trial.suggest_int('bagging_freq', 1, 10),
            'lambda_l1': trial.suggest_float('lambda_l1', 1e-8, 10.0, log=True),
            'lambda_l2': trial.suggest_float('lambda_l2', 1e-8, 10.0, log=True),
            'objective': 'binary',
            'metric': 'auc',
            'verbosity': -1,
            'random_state': 42
        }
        
        # Обучаем модель
        model = lgb.LGBMClassifier(**params)
        model.fit(X_train_scaled, y_train)
        
        # Предсказываем на тестовой выборке
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)
        
        # Метрики
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        accuracy = (y_pred == y_test).mean()
        f1 = f1_score(y_test, y_pred)
        
        # Логируем в MLflow (только метрики и параметры, без модели)
        with mlflow.start_run(experiment_id=experiment_id, nested=True):
            mlflow.log_params(params)
            mlflow.log_metrics({
                'roc_auc': roc_auc,
                'accuracy': accuracy,
                'f1_score': f1,
                'trial_number': trial.number
            })
        
        # Логируем результаты
        logger.info(f"Trial {trial.number}: ROC-AUC={roc_auc:.4f}, Accuracy={accuracy:.4f}, F1={f1:.4f}")
        
        return roc_auc  # Оптимизируем по ROC-AUC
    
    # Создаем study
    study = optuna.create_study(
        direction='maximize',
        study_name='wildfire_prediction_optimization'
    )
    
    # Запускаем оптимизацию
    study.optimize(objective, n_trials=20, timeout=1800)  # 20 trials, 30 min timeout
    
    # Лучшие параметры
    best_params = study.best_params
    best_score = study.best_value
    
    logger.info(f"Best ROC-AUC: {best_score:.4f}")
    logger.info(f"Best parameters: {best_params}")
    
    # Обучаем финальную модель с лучшими параметрами
    final_model = lgb.LGBMClassifier(**best_params, random_state=42)
    final_model.fit(X_train_scaled, y_train)
    
    # Финальная оценка
    y_pred_proba = final_model.predict_proba(X_test_scaled)[:, 1]
    y_pred = final_model.predict(X_test_scaled)
    
    final_roc_auc = roc_auc_score(y_test, y_pred_proba)
    final_accuracy = (y_pred == y_test).mean()
    final_f1 = f1_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = dict(zip(feature_columns, final_model.feature_importances_))
    
    # Логируем финальную модель в MLflow (только метрики и параметры)
    with mlflow.start_run(experiment_id=experiment_id):
        mlflow.log_params(best_params)
        mlflow.log_metrics({
            'final_roc_auc': final_roc_auc,
            'final_accuracy': final_accuracy,
            'final_f1_score': final_f1,
            'best_roc_auc': best_score,
            'n_trials': len(study.trials)
        })
        
        # Логируем feature importance
        for feature, importance in feature_importance.items():
            mlflow.log_metric(f"importance_{feature}", importance)
        
        # Логируем метаданные как параметры
        mlflow.log_param("feature_columns", str(feature_columns))
        mlflow.log_param("study_name", study.study_name)
        mlflow.log_param("total_samples", training_data['total_samples'])
        mlflow.log_param("positive_samples", training_data['positive_samples'])
        mlflow.log_param("negative_samples", training_data['negative_samples'])
        
        run_id = mlflow.active_run().info.run_id
        logger.info(f"MLflow run ID: {run_id}")
    
    # Сохраняем результаты
    optimization_results = {
        'best_params': best_params,
        'best_roc_auc': best_score,
        'final_roc_auc': final_roc_auc,
        'final_accuracy': final_accuracy,
        'final_f1_score': final_f1,
        'feature_importance': feature_importance,
        'n_trials': len(study.trials),
        'study_name': study.study_name,
        'mlflow_run_id': run_id,
        'experiment_name': experiment_name
    }
    
    # Сохраняем модель сразу в MinIO
    with tempfile.TemporaryDirectory() as temp_dir:
        # Сохраняем модель
        model_path = os.path.join(temp_dir, 'wildfire_model.pkl')
        joblib.dump(final_model, model_path)
        
        # Сохраняем scaler
        scaler_path = os.path.join(temp_dir, 'scaler.pkl')
        joblib.dump(scaler, scaler_path)
        
        # Загружаем в MinIO
        s3_hook = S3Hook(aws_conn_id='minio_default')
        bucket_name = 'models'
        
        # Создаем bucket если не существует
        try:
            s3_hook.create_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
        except:
            logger.info(f"Bucket {bucket_name} already exists")
        
        # Загружаем файлы
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        model_key = f'wildfire_model_{timestamp}.pkl'
        scaler_key = f'scaler_{timestamp}.pkl'
        
        s3_hook.load_file(
            filename=model_path,
            key=model_key,
            bucket_name=bucket_name
        )
        
        s3_hook.load_file(
            filename=scaler_path,
            key=scaler_key,
            bucket_name=bucket_name
        )
        
        # Сохраняем ссылки на файлы
        model_files = {
            'model_key': model_key,
            'scaler_key': scaler_key,
            'bucket_name': bucket_name,
            'timestamp': timestamp
        }
        
        logger.info(f"Model saved to MinIO: {bucket_name}/{model_key}")
        logger.info(f"Scaler saved to MinIO: {bucket_name}/{scaler_key}")
    
    context['task_instance'].xcom_push(key='optimization_results', value=optimization_results)
    context['task_instance'].xcom_push(key='model_files', value=model_files)
    
    logger.info(f"Optimization completed: Best ROC-AUC={best_score:.4f}, Final ROC-AUC={final_roc_auc:.4f}, Final F1={final_f1:.4f}")
    logger.info(f"MLflow run ID: {run_id}")
    
    return f"Optimization completed: Best ROC-AUC={best_score:.4f}, Final ROC-AUC={final_roc_auc:.4f}, Final F1={final_f1:.4f}, MLflow Run ID: {run_id}"

optimize_model = PythonOperator(
    task_id='optimize_hyperparameters',
    python_callable=optimize_hyperparameters,
    dag=dag
)

# ============================================================================
# TASK 3: Сохранение модели в MinIO
# ============================================================================

def save_model_to_minio(**context):
    """
    Сохранение метаданных модели в MinIO bucket 'models'.
    Модель уже сохранена в optimize_hyperparameters.
    """
    logger.info("Saving model metadata to MinIO")
    
    # Получаем результаты
    optimization_results = context['task_instance'].xcom_pull(key='optimization_results', task_ids='optimize_hyperparameters')
    model_files = context['task_instance'].xcom_pull(key='model_files', task_ids='optimize_hyperparameters')
    training_data = context['task_instance'].xcom_pull(key='training_data', task_ids='prepare_training_data')
    
    # Создаем временную директорию
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Сохраняем метаданные
        metadata = {
            'model_type': 'LightGBM',
            'feature_columns': training_data['feature_columns'],
            'optimization_results': optimization_results,
            'training_stats': {
                'sample_size': training_data['sample_size'],
                'total_samples': training_data['total_samples'],
                'positive_samples': training_data['positive_samples'],
                'negative_samples': training_data['negative_samples']
            },
            'mlflow_info': {
                'run_id': optimization_results.get('mlflow_run_id'),
                'experiment_name': optimization_results.get('experiment_name'),
                'tracking_uri': 'http://92.51.23.44:5000'
            },
            'model_files': model_files,
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        metadata_path = os.path.join(temp_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Загружаем в MinIO
        s3_hook = S3Hook(aws_conn_id='minio_default')
        bucket_name = 'models'
        
        # Загружаем метаданные
        metadata_key = f'model_metadata_{model_files["timestamp"]}.json'
        
        s3_hook.load_file(
            filename=metadata_path,
            key=metadata_key,
            bucket_name=bucket_name
        )
        
        logger.info(f"Metadata saved to MinIO: {bucket_name}/{metadata_key}")
        
        return f"Model metadata saved to MinIO: {metadata_key} (ROC-AUC: {optimization_results['final_roc_auc']:.4f})"

save_model = PythonOperator(
    task_id='save_model_to_minio',
    python_callable=save_model_to_minio,
    dag=dag
)

# ============================================================================
# TASK 4: Валидация модели
# ============================================================================

def validate_model(**context):
    """
    Финальная валидация модели и генерация отчетов.
    """
    logger.info("Validating model performance")
    
    # Получаем данные
    training_data = context['task_instance'].xcom_pull(key='training_data', task_ids='prepare_training_data')
    optimization_results = context['task_instance'].xcom_pull(key='optimization_results', task_ids='optimize_hyperparameters')
    model_files = context['task_instance'].xcom_pull(key='model_files', task_ids='save_model_to_minio')
    
    X_test = pd.DataFrame.from_dict(training_data['X_test'])
    y_test = pd.Series(training_data['y_test'])
    
    # Получаем модель
    final_model = context['task_instance'].xcom_pull(key='final_model', task_ids='optimize_hyperparameters')
    scaler = context['task_instance'].xcom_pull(key='scaler', task_ids='optimize_hyperparameters')
    
    # Предсказания
    X_test_scaled = scaler.transform(X_test)
    y_pred = final_model.predict(X_test_scaled)
    y_pred_proba = final_model.predict_proba(X_test_scaled)[:, 1]
    
    # Метрики
    classification_rep = classification_report(y_test, y_pred, output_dict=True)
    conf_matrix = confusion_matrix(y_test, y_pred)
    
    # Feature importance
    feature_importance = optimization_results['feature_importance']
    top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Генерируем отчет
    validation_report = {
        'model_performance': {
            'roc_auc': optimization_results['final_roc_auc'],
            'accuracy': optimization_results['final_accuracy'],
            'precision': classification_rep['weighted avg']['precision'],
            'recall': classification_rep['weighted avg']['recall'],
            'f1_score': classification_rep['weighted avg']['f1-score']
        },
        'confusion_matrix': conf_matrix.tolist(),
        'classification_report': classification_rep,
        'top_features': top_features,
        'model_files': model_files,
        'training_stats': training_data,
        'validation_timestamp': datetime.now().isoformat()
    }
    
    context['task_instance'].xcom_push(key='validation_report', value=validation_report)
    
    logger.info(f"Model validation completed:")
    logger.info(f"  ROC-AUC: {optimization_results['final_roc_auc']:.4f}")
    logger.info(f"  Accuracy: {optimization_results['final_accuracy']:.4f}")
    logger.info(f"  Top features: {[f[0] for f in top_features[:5]]}")
    
    return f"Model validated: ROC-AUC={optimization_results['final_roc_auc']:.4f}, Accuracy={optimization_results['final_accuracy']:.4f}"

validate_model_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model,
    dag=dag
)

# ============================================================================
# Завершение
# ============================================================================

end_training = EmptyOperator(
    task_id='end_ml_training',
    dag=dag
)

# ============================================================================
# Определение зависимостей
# ============================================================================

prepare_data >> optimize_model >> save_model >> validate_model_task >> end_training 