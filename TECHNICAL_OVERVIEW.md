# 🔧 Технический обзор Wildfire Prediction System

## 🏗️ Архитектура

### Микросервисная архитектура

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │
│   (React/Vue)   │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   MinIO S3      │
                       │   (Database)    │    │   (Storage)     │
                       └─────────────────┘    └─────────────────┘
                              ▲                        ▲
                              │                        │
                              └────────────┬───────────┘
                                           │
                                    ┌─────────────────┐
                                    │   ML Pipeline   │
                                    │   (Airflow)     │
                                    └─────────────────┘
```

### Компоненты системы

#### Backend API (FastAPI)
- **Порт**: 8000
- **Фреймворк**: FastAPI с Pydantic
- **База данных**: PostgreSQL через SQLAlchemy
- **Аутентификация**: JWT токены
- **Документация**: Swagger UI на `/docs`

#### ML Pipeline (Airflow)
- **Порт**: 8080
- **Оркестрация**: Apache Airflow
- **Обработка данных**: pandas, xarray, numpy
- **ML**: scikit-learn, joblib
- **Хранилище**: MinIO S3

#### База данных (PostgreSQL)
- **Схема**: `fireforceai`
- **Миграции**: Alembic
- **Основные таблицы**:
  - `fire_events` - данные о пожарах
  - `weather_data` - метеорологические данные
  - `predictions` - результаты прогнозов
  - `training_features` - признаки для ML

## 📊 Схема базы данных

### Основные таблицы

```sql
-- Данные о пожарах
CREATE TABLE fireforceai.fire_events (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    fire_date DATE,
    fire_size DECIMAL(10, 2),
    confidence DECIMAL(3, 2),
    source VARCHAR(50)
);

-- Метеорологические данные
CREATE TABLE fireforceai.weather_data (
    id SERIAL PRIMARY KEY,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    dt TIMESTAMP,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    precipitation DECIMAL(8, 2),
    data_source VARCHAR(20)
);

-- Прогнозы пожаров
CREATE TABLE fireforceai.predictions (
    id UUID PRIMARY KEY,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    risk_level VARCHAR(20),
    risk_percentage DECIMAL(5, 2),
    confidence DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔄 Data Pipeline

### Airflow DAGs

#### 1. wildfire_historical_fire_data_dag
- **Цель**: Загрузка исторических данных о пожарах
- **Источник**: CSV файлы из MinIO
- **Обработка**: Очистка, валидация, генерация негативных сэмплов
- **Результат**: Таблица `fire_events`

#### 2. wildfire_historical_weather_data_dag
- **Цель**: Загрузка метеорологических данных ERA5
- **Источник**: NetCDF файлы из MinIO
- **Обработка**: Фильтрация по времени, агрегация, прямая запись в БД
- **Результат**: Таблицы `weather_data_instant`, `weather_data_accum`

#### 3. wildfire_ml_pipeline_dag
- **Цель**: Обучение и развертывание ML моделей
- **Вход**: Объединенные данные пожаров и погоды
- **Обработка**: Feature engineering, обучение модели, валидация
- **Результат**: Сохраненная модель в MinIO

### Оптимизации производительности

#### Обработка больших файлов
```python
# Чанковая обработка NetCDF файлов
ds = xr.open_dataset(file_path, chunks={
    "valid_time": 50, 
    "latitude": 25, 
    "longitude": 25
})

# Прямая запись в БД чанками
for chunk in processed_data.chunks():
    df_chunk = chunk.to_dataframe()
    engine.execute(insert_stmt, df_chunk.to_dict('records'))
```

#### Управление памятью
- **Streaming обработка** больших файлов
- **Временные файлы** для промежуточных результатов
- **Connection pooling** для базы данных
- **Garbage collection** после обработки чанков

## 🤖 Machine Learning

### Текущая модель

#### Демо-модель (RandomForest)
```python
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
```

#### Признаки (Features)
```python
feature_names = [
    "latitude", "longitude",
    "current_temperature", "current_humidity",
    "current_wind_speed", "current_precipitation",
    "avg_temperature_7d", "avg_humidity_7d",
    "avg_wind_speed_7d", "total_precipitation_7d",
    "temperature_trend", "humidity_trend"
]
```

#### Модель в продакшене
- **Алгоритм**: RandomForestClassifier
- **Метрики**: accuracy=0.85, precision=0.82, recall=0.88
- **Версия**: 1.0.0
- **Размер**: 1.46 MB

### Процесс предсказания

1. **Получение координат** от пользователя
2. **Запрос погодных данных** через ERA5 API
3. **Подготовка признаков** для модели
4. **Предсказание** риска пожара
5. **Расчет уверенности** на основе качества данных
6. **Возврат результата** с рекомендациями

## 🌤️ Интеграция с ERA5 API

### Конфигурация
```python
# wildfire-backend/.env
ERA5_API_KEY=your_era5_api_key_here
ERA5_API_URL=https://cds.climate.copernicus.eu/api/v2
```

### Запрос к API
```python
result = cds_client.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': '2m_temperature',
        'year': 2025, 'month': 7, 'day': 29,
        'time': '12:00',
        'area': [lat+0.1, lon-0.1, lat-0.1, lon+0.1],
        'format': 'netcdf',
    }
)
```

### Fallback механизм
- **Первичный источник**: ERA5 API
- **Резервный источник**: Open-Meteo API
- **Логирование**: Детальная статистика запросов
- **Мониторинг**: Endpoint `/api/v1/predictions/era5-stats`

## 🔧 API Endpoints

### Прогнозирование
```http
POST /api/v1/predictions/request
Content-Type: application/json

{
  "latitude": 55.7558,
  "longitude": 37.6176
}
```

### Ответ
```json
{
  "risk_level": "high",
  "risk_percentage": 51.3,
  "confidence": 78.5,
  "factors": ["Высокая температура", "Низкая влажность"],
  "recommendations": ["Усилить мониторинг"],
  "weather_data_source": "era5",
  "model_version": "1.0.0"
}
```

### Мониторинг
```http
GET /api/v1/health
GET /api/v1/predictions/era5-stats
GET /api/v1/health/services
```

## 📈 Мониторинг и логирование

### Логирование
```python
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
```

### Метрики ERA5 API
```python
era5_stats = {
    "request_count": 0,
    "success_count": 0,
    "failure_count": 0,
    "total_duration": 0.0
}
```

## 🚀 Развертывание

### Локальная разработка
```bash
# Клонирование
git clone <repository>
cd cursorfire

# Настройка окружения
cp wildfire-backend/.env.example wildfire-backend/.env
# Редактируйте .env файл

# Запуск через Docker
docker-compose up -d

# Запуск Backend
cd wildfire-backend
python -m uvicorn app.main:app --reload
```

### Продакшн развертывание
```bash
# Сборка образов
docker-compose -f docker-compose.prod.yml build

# Запуск в продакшне
docker-compose -f docker-compose.prod.yml up -d

# Применение миграций
docker-compose exec backend alembic upgrade head
```

## 🔒 Безопасность

### Переменные окружения
- **Секреты**: ERA5 API ключи, пароли БД
- **Конфигурация**: URL сервисов, порты
- **Логирование**: Уровни логирования

### API безопасность
- **Rate limiting**: Ограничение запросов
- **CORS**: Настройка cross-origin запросов
- **Validation**: Pydantic валидация входных данных

## 📊 Производительность

### Оптимизации
- **Connection pooling**: SQLAlchemy engine
- **Кэширование**: Redis для частых запросов
- **Асинхронность**: FastAPI async/await
- **Чанковая обработка**: Большие файлы по частям

### Метрики
- **Время ответа API**: < 2 секунды
- **Точность модели**: > 85%
- **Доступность**: 99.9%
- **Пропускная способность**: 1000+ запросов/минуту

---

**Технический обзор** - Детальное описание архитектуры и компонентов системы Wildfire Prediction System. 