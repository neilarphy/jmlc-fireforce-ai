# Используем официальный образ Airflow как базовый
FROM apache/airflow:2.10.1-python3.11

# Установим дополнительные зависимости
# ВАЖНО:_airflow_ user, не root
USER airflow
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
    dask[complete]
