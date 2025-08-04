# Airflow Setup для Wildfire Prediction System

## 📋 **Обзор DAG'ов**

### **Исторические данные (однократная загрузка):**

1. **`wildfire_historical_fire_data`** - Загрузка исторических данных о пожарах из CSV
   - Загружает `russia_fires_hist.csv` из MinIO
   - Создает базовые ML признаки
   - Создает статистику по пожарам
   - Время выполнения: ~5-10 минут

2. **`wildfire_historical_weather_data`** - Загрузка исторических метеоданных из ERA5
   - Обрабатывает `era5_instant_3years.nc` и `era5_accum_3years.nc`
   - Использует `xarray` для обработки .nc файлов
   - Обновляет ML признаки с погодными данными
   - Время выполнения: ~30-60 минут (тяжелые файлы)

### **Ежедневные DAG'и:**

3. **`wildfire_data_pipeline`** - Ежедневная обработка новых данных
4. **`wildfire_ml_pipeline`** - Еженедельное обучение ML моделей
5. **`wildfire_monitoring`** - Почасовый мониторинг системы

## 🔧 **Настройка Connections**

### **1. PostgreSQL Connection (`wildfire_db`)**
```
Connection Id: wildfire_db
Connection Type: Postgres
Host: localhost (или ваш PostgreSQL сервер)
Schema: wildfire (или ваша схема)
Login: ваш_пользователь
Password: ваш_пароль
Port: 5432
```

### **2. MinIO Connection (`minio_default`)**
```
Connection Id: minio_default
Connection Type: Amazon Web Services
Login: minioadmin (или ваш access key)
Password: minioadmin (или ваш secret key)
Host: localhost:9000 (или ваш MinIO endpoint)
```

### **3. HTTP API Connection (`wildfire_api`)**
```
Connection Id: wildfire_api
Connection Type: HTTP
Host: http://localhost:8000 (или ваш FastAPI сервер)
```

## 📊 **Структура таблиц**

### **Основные таблицы:**
- `fireforceai.historical_fires` - Исторические данные о пожарах
- `fireforceai.raw_weather_data` - Сырые метеорологические данные
- `fireforceai.training_features` - Признаки для ML обучения
- `fireforceai.fire_statistics` - Статистика пожаров

## 🚀 **Порядок запуска**

### **Шаг 1: Загрузка исторических данных о пожарах**
```bash
# В Airflow UI запустите DAG вручную:
wildfire_historical_fire_data
```

**Ожидаемый результат:**
- ~50,000-100,000 записей о пожарах
- Базовые ML признаки созданы
- Статистика по годам/месяцам

### **Шаг 2: Загрузка исторических метеоданных**
```bash
# В Airflow UI запустите DAG вручную:
wildfire_historical_weather_data
```

**Ожидаемый результат:**
- ~100,000-200,000 записей погодных данных
- ML признаки обновлены с погодными данными
- Полное покрытие 3 лет (2021-2024)

### **Шаг 3: Проверка данных**
```sql
-- Проверка загруженных данных
SELECT COUNT(*) FROM fireforceai.historical_fires;
SELECT COUNT(*) FROM fireforceai.raw_weather_data;
SELECT COUNT(*) FROM fireforceai.training_features;

-- Проверка покрытия погодными данными
SELECT 
    COUNT(*) as total_samples,
    COUNT(*) FILTER (WHERE avg_temperature IS NOT NULL) as with_weather
FROM fireforceai.training_features;
```

## 📁 **MinIO Bucket Structure**

```
fire-datasets/
├── russia_fires_hist.csv          # Исторические данные о пожарах (37.7 MiB)
├── era5_instant_3years.nc         # Мгновенные метеоданные (293.8 MiB)
└── era5_accum_3years.nc           # Накопленные метеоданные (39.9 MiB)
```

## 🔍 **Логирование и мониторинг**

### **Проверка логов:**
```bash
# В Airflow UI -> DAGs -> Task Instance -> Log
# Или через CLI:
airflow tasks logs wildfire_historical_fire_data load_historical_fire_data_from_minio latest
```

### **XCom данные:**
- `fire_data_stats` - Статистика загруженных данных о пожарах
- `weather_data_stats` - Статистика загруженных метеоданных
- `feature_stats` - Статистика созданных ML признаков

## ⚠️ **Требования к зависимостям**

### **Установка дополнительных пакетов:**
```bash
pip install xarray netCDF4 minio pandas numpy
```

### **Проверка установки:**
```python
import xarray as xr
import pandas as pd
import numpy as np
from minio import Minio
print("✅ Все зависимости установлены")
```

## 🛠️ **Troubleshooting**

### **Проблема: Ошибка импорта xarray**
```bash
# Решение: Установите зависимости
pip install xarray netCDF4
```

### **Проблема: Ошибка подключения к MinIO**
```bash
# Проверьте connection в Airflow UI
# Убедитесь, что MinIO запущен и доступен
```

### **Проблема: Недостаточно памяти для обработки ERA5**
```python
# В DAG добавьте chunking для больших файлов:
ds = xr.open_dataset(nc_file_path, chunks={"valid_time": 1})
```

### **Проблема: Ошибка PostgreSQL**
```sql
-- Проверьте подключение к БД:
SELECT 1;
-- Проверьте схему:
SELECT * FROM information_schema.schemata WHERE schema_name = 'fireforceai';
```

## 📈 **Мониторинг производительности**

### **Метрики для отслеживания:**
- Время выполнения каждого DAG
- Количество загруженных записей
- Покрытие данных по времени и географии
- Качество данных (валидация)

### **Алерты:**
- Ошибки загрузки данных
- Недостаточное покрытие метеоданными
- Проблемы с качеством данных

## 🔄 **Следующие шаги**

После успешной загрузки исторических данных:

1. **Настройте ежедневные DAG'и** для обработки новых данных
2. **Запустите ML pipeline** для обучения моделей
3. **Настройте мониторинг** для отслеживания качества данных
4. **Создайте дашборды** для визуализации результатов

## 📞 **Поддержка**

При возникновении проблем:
1. Проверьте логи в Airflow UI
2. Убедитесь в корректности connections
3. Проверьте доступность MinIO и PostgreSQL
4. Убедитесь в установке всех зависимостей 