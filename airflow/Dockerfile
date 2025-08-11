# Используем официальный образ Airflow как базовый
FROM apache/airflow:2.10.1-python3.11

# Переключаемся на root для установки системных пакетов
USER root

# Устанавливаем системные зависимости для LightGBM
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Переключаемся обратно на airflow user
USER airflow

# Установим дополнительные зависимости
RUN pip install --no-cache-dir \
    structlog \
    celery \
    redis \
    boto3 \
    apache-airflow-providers-amazon \
    smart_open \
    xarray \
    netCDF4 \
    minio \
    pandas \
    numpy \
    dask[complete] \
    lightgbm \
    optuna \
    mlflow \
    scikit-learn \
    joblib
