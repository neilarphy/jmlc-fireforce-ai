# Wildfire Prediction Backend

Backend API для системы прогнозирования лесных пожаров с использованием ML моделей и метеорологических данных ERA5.

## Возможности

- 🔥 **Прогнозирование пожаров** - ML модель для оценки риска пожаров
- 🌤️ **ERA5 интеграция** - получение реальных метеорологических данных
- 📊 **Исторические данные** - анализ трендов погоды за 7 дней
- 🗄️ **PostgreSQL** - хранение предсказаний и метаданных
- 🔐 **Аутентификация** - JWT токены для безопасности

## Установка

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd wildfire-backend
```

### 2. Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл `.env`:
```env
# База данных
DATABASE_URL=postgresql://wildfire_user:password@localhost:5432/wildfire

# ERA5 API (обязательно для реальных данных)
ERA5_API_KEY=your_era5_api_key_here
ERA5_API_URL=https://cds.climate.copernicus.eu/api/v2

# JWT секреты
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Другие настройки
DEBUG=True
LOG_LEVEL=INFO
```

### 5. Настройка ERA5 API

#### Получение API ключа
1. Зарегистрируйтесь на [CDS (Climate Data Store)](https://cds.climate.copernicus.eu/)
2. Перейдите в раздел "API"
3. Скопируйте ваш API ключ
4. Добавьте ключ в переменную `ERA5_API_KEY`

#### Настройка .cdsapirc
Создайте файл `~/.cdsapirc`:
```ini
url: https://cds.climate.copernicus.eu/api/v2
key: your_era5_api_key_here
```

### 6. Миграции базы данных
```bash
alembic upgrade head
```

### 7. Запуск сервера
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Прогнозирование пожаров

#### Создать предсказание
```http
POST /api/v1/predictions
Content-Type: application/json

{
  "latitude": 55.7558,
  "longitude": 37.6176,
  "description": "Москва, центр"
}
```

#### Получить статус предсказания
```http
GET /api/v1/predictions/status/{prediction_id}
```

#### История предсказаний
```http
GET /api/v1/predictions/history?limit=50&offset=0
```

#### Статистика предсказаний
```http
GET /api/v1/predictions/stats
```

## Структура данных

### Погодные признаки
Система использует следующие признаки для ML модели:

- **Географические**: latitude, longitude
- **Текущие**: temperature, humidity, wind_speed, precipitation
- **Исторические (7 дней)**: avg_temperature, avg_humidity, avg_wind_speed, total_precipitation
- **Тренды**: temperature_trend, humidity_trend

### Уровни риска
- **low** (0-25%): Низкий риск
- **medium** (25-50%): Средний риск
- **high** (50-75%): Высокий риск
- **critical** (75-100%): Критический риск

## ML Модель

### Особенности модели
- **Алгоритм**: Random Forest / Gradient Boosting
- **Признаки**: 12 метеорологических параметров
- **Обучение**: на исторических данных пожаров 2020-2021
- **Версия**: 1.0.0

### Обновление модели
```bash
# Обучение новой модели
python scripts/train_model.py

# Развертывание модели
python scripts/deploy_model.py
```

## Мониторинг

### Логи
- **Уровень**: INFO
- **Формат**: JSON
- **Ротация**: ежедневно

### Метрики
- Количество предсказаний
- Точность модели
- Время ответа API
- Использование ERA5 API

## Разработка

### Структура проекта
```
wildfire-backend/
├── app/
│   ├── core/           # Конфигурация и БД
│   ├── models/         # SQLAlchemy модели
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес-логика
│   └── main.py         # Точка входа
├── alembic/            # Миграции БД
├── tests/              # Тесты
└── requirements.txt    # Зависимости
```

### Запуск тестов
```bash
pytest tests/
```

### Линтинг
```bash
flake8 app/
black app/
```

## Лицензия

MIT License 