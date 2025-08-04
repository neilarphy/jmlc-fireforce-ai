# 🔥 Wildfire Prediction System

Система прогнозирования лесных пожаров на основе машинного обучения и метеорологических данных.

## 📋 Описание проекта

Wildfire Prediction System - это комплексная система для прогнозирования риска лесных пожаров, использующая современные технологии машинного обучения, обработки больших данных и интеграции с внешними API.

### 🎯 Основные цели

- **Прогнозирование риска пожаров** на основе метеорологических данных
- **Интеграция с ERA5 API** для получения актуальных погодных данных
- **Автоматизированная обработка данных** через Apache Airflow
- **Масштабируемая архитектура** с использованием микросервисов
- **Реальное время** - мгновенные прогнозы по координатам

## 🏗️ Архитектура системы

### Компоненты системы

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

### Технологический стек

- **Backend**: FastAPI, Python 3.11
- **Database**: PostgreSQL с Alembic миграциями
- **ML Pipeline**: Apache Airflow, scikit-learn
- **Storage**: MinIO (S3-совместимое)
- **Weather Data**: ERA5 API (Copernicus Climate Data Store)
- **Monitoring**: MLflow для отслеживания экспериментов

## 📊 Функциональность

### 🔥 Прогнозирование пожаров

Система предоставляет API для получения прогнозов риска пожаров:

```bash
curl -X POST "http://localhost:8000/api/v1/predictions/request" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6176}'
```

**Ответ:**
```json
{
  "risk_level": "high",
  "risk_percentage": 51.3,
  "confidence": 78.5,
  "factors": ["Высокая температура воздуха", "Низкая влажность"],
  "recommendations": ["Усилить мониторинг территории"],
  "weather_data_source": "era5",
  "model_version": "1.0.0"
}
```

### 🌤️ Интеграция с ERA5 API

- **Реальные погодные данные** из Copernicus Climate Data Store
- **Автоматическое получение** текущих и исторических данных
- **Fallback механизм** на Open-Meteo API при недоступности ERA5
- **Детальная статистика** запросов к API

### 📈 Обработка данных

#### Исторические данные пожаров
- **Загрузка** из CSV файлов через Airflow
- **Очистка и валидация** данных
- **Генерация негативных сэмплов** для балансировки датасета
- **Создание признаков** для ML модели

#### Метеорологические данные
- **Загрузка ERA5 данных** за 2020-2021 годы
- **Обработка NetCDF файлов** с помощью xarray
- **Оптимизация памяти** для больших файлов (350MB+)
- **Прямая запись в БД** чанками для экономии памяти

### 🤖 Машинное обучение

#### Текущая модель
- **Демо-модель**: RandomForestClassifier для тестирования
- **Признаки**: температура, влажность, ветер, осадки, координаты
- **Метрики**: accuracy, precision, recall, F1-score

#### Планы развития
- **Обучение на реальных данных** после загрузки исторических данных
- **Гиперпараметрическая оптимизация** через Optuna
- **Автоматическое переобучение** модели
- **A/B тестирование** моделей

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+
- PostgreSQL
- MinIO (S3-совместимое хранилище)

### Установка и запуск

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd cursorfire
```

2. **Настройка переменных окружения**
```bash
# wildfire-backend/.env
ERA5_API_KEY=your_era5_api_key_here
ERA5_API_URL=https://cds.climate.copernicus.eu/api/v2
DATABASE_URL=postgresql://wildfire_user:wildfire_password@localhost:5432/wildfire_db
```

3. **Запуск через Docker Compose**
```bash
docker-compose up -d
```

4. **Запуск Airflow DAGs**
```bash
# Загрузка исторических данных пожаров
# Загрузка метеорологических данных
# Создание ML признаков
```

5. **Запуск Backend API**
```bash
cd wildfire-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Структура проекта

```
cursorfire/
├── wildfire-backend/           # FastAPI Backend
│   ├── app/
│   │   ├── core/              # Конфигурация и база данных
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── routers/           # API endpoints
│   │   ├── schemas/           # Pydantic схемы
│   │   ├── services/          # Бизнес-логика
│   │   └── tasks/             # Celery задачи
│   ├── alembic/               # Миграции базы данных
│   ├── models/                # ML модели (joblib файлы)
│   ├── requirements.txt       # Python зависимости
│   ├── Dockerfile             # Docker образ
│   ├── docker-compose.yml     # Backend сервисы (API + Worker)
│   ├── run.py                 # Запуск приложения
│   └── run_worker.py          # Запуск Celery воркера
├── frontend/                  # Vue.js + Quasar Frontend
│   ├── src/
│   │   ├── components/        # Vue компоненты
│   │   ├── pages/            # Страницы приложения
│   │   ├── layouts/          # Макеты страниц
│   │   ├── router/           # Vue Router конфигурация
│   │   ├── stores/           # Pinia stores
│   │   ├── services/         # API сервисы
│   │   ├── utils/            # Утилиты
│   │   ├── css/              # Стили
│   │   └── assets/           # Статические ресурсы
│   ├── public/               # Публичные файлы
│   ├── package.json          # Node.js зависимости
│   ├── quasar.config.js      # Quasar конфигурация
│   └── Dockerfile            # Docker образ
├── services/                  # Основные сервисы (PostgreSQL, Redis, MinIO, MLflow)
│   ├── docker-compose.yml    # Основные сервисы
│   └── mlflow/               # MLflow конфигурация
├── airflow/                  # Apache Airflow DAGs
│   ├── dags/
│   │   ├── wildfire_historical_fire_data_dag.py
│   │   ├── wildfire_historical_weather_data_dag.py
│   │   ├── wildfire_ml_pipeline_dag.py
│   │   ├── wildfire_data_pipeline_dag.py
│   │   ├── wildfire_monitoring_dag.py
│   │   └── test_permissions_dag.py
│   ├── plugins/              # Airflow плагины
│   ├── requirements.txt      # Python зависимости
│   └── docker-compose.yml   # Airflow контейнеры
├── oldcode/                  # Архивная версия (не используется)
├── notebooks/                # Jupyter notebooks
│   └── forestfire.ipynb     # Анализ и обучение моделей
├── docker-compose.yml        # Airflow контейнеры (корень)
├── requirements.txt          # Общие Python зависимости
├── README.md                 # Основная документация
├── TECHNICAL_OVERVIEW.md     # Технический обзор
└── BUSINESS_OVERVIEW.md      # Бизнес-документация
```

### 🐳 Docker архитектура

#### 1. **services/docker-compose.yml** - Основные сервисы
- **PostgreSQL** (порт 5433) - основная БД приложения
- **Redis** (порт 6379) - кэш и очереди
- **MinIO** (порты 9000, 9001) - S3-совместимое хранилище
- **MLflow** (порт 5000) - отслеживание ML экспериментов

#### 2. **wildfire-backend/docker-compose.yml** - Backend приложение
- **API** (порт 8000) - FastAPI приложение
- **Worker** - Celery воркер для асинхронных задач
- Подключается к сервисам из services/

#### 3. **docker-compose.yml** (корень) - Airflow
- **Airflow Webserver** (порт 8080)
- **Airflow Scheduler**
- **Airflow Worker**
- **Airflow Triggerer**
- **Airflow PostgreSQL** - отдельная БД для Airflow

## 🔧 API Endpoints

### Прогнозирование

- `POST /api/v1/predictions/request` - Запрос прогноза по координатам
- `GET /api/v1/predictions/status/{task_id}` - Статус асинхронного прогноза
- `GET /api/v1/predictions/era5-stats` - Статистика ERA5 API запросов

### Данные

- `GET /api/v1/data/fire-events` - Исторические данные пожаров
- `GET /api/v1/data/weather` - Метеорологические данные
- `POST /api/v1/data/upload` - Загрузка новых данных

### Мониторинг

- `GET /api/v1/health` - Проверка здоровья системы
- `GET /api/v1/health/services` - Статус всех сервисов

## 📊 Мониторинг и логирование

### Логирование
- **Structured logging** с контекстом
- **Уровни логирования**: DEBUG, INFO, WARNING, ERROR
- **Файлы логов**: `app.log` в wildfire-backend

### Метрики
- **ERA5 API статистика**: количество запросов, успешность, время ответа
- **ML модель**: точность, уверенность, время предсказания
- **Системные метрики**: использование памяти, CPU, диск

## 🔄 CI/CD Pipeline

### Автоматизация
- **Тестирование**: pytest для unit и integration тестов
- **Линтинг**: flake8, black для качества кода
- **Миграции**: автоматическое применение Alembic миграций
- **Деплой**: Docker контейнеры для всех сервисов

## 🛠️ Разработка

### Локальная разработка

1. **Настройка виртуального окружения**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

3. **Настройка базы данных**
```bash
cd wildfire-backend
alembic upgrade head
```

4. **Запуск тестов**
```bash
pytest tests/
```

### Структура кода

- **Type hints** для всех функций
- **Docstrings** для всех классов и методов
- **Error handling** с детальными сообщениями
- **Configuration management** через Pydantic Settings

## 📈 Производительность

### Оптимизации

- **Кэширование** погодных данных
- **Асинхронные запросы** к внешним API
- **Чанковая обработка** больших файлов
- **Connection pooling** для базы данных

### Масштабируемость

- **Микросервисная архитектура**
- **Горизонтальное масштабирование** через Docker
- **Load balancing** для API endpoints
- **Database sharding** для больших объемов данных

## 🔒 Безопасность

### Аутентификация и авторизация
- **JWT токены** для API доступа
- **Role-based access control** (RBAC)
- **API rate limiting** для предотвращения злоупотреблений

### Защита данных
- **Environment variables** для секретов
- **Database encryption** для чувствительных данных
- **HTTPS** для всех внешних соединений

## 🚀 Планы развития

### Краткосрочные цели (1-3 месяца)
- [ ] Обучение модели на реальных данных
- [ ] Интеграция с дополнительными источниками данных
- [ ] Улучшение точности прогнозов
- [ ] Разработка веб-интерфейса

### Среднесрочные цели (3-6 месяцев)
- [ ] Реализация real-time мониторинга
- [ ] Интеграция с системами оповещения
- [ ] Мобильное приложение
- [ ] API для внешних интеграций

### Долгосрочные цели (6+ месяцев)
- [ ] Расширение на другие регионы
- [ ] Интеграция с спутниковыми данными
- [ ] Продвинутые ML модели (Deep Learning)
- [ ] Коммерциализация продукта

## 🤝 Вклад в проект

### Как внести вклад
1. Fork репозитория
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

### Стандарты кода
- **PEP 8** для Python кода
- **Type hints** для всех функций
- **Docstrings** для всех публичных методов
- **Тесты** для новой функциональности

## 📞 Контакты

- **Email**: data-team@wildfire-prediction.com
- **Issues**: GitHub Issues для багов и предложений
- **Discussions**: GitHub Discussions для общих вопросов

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

**Wildfire Prediction System** - Инновационное решение для прогнозирования лесных пожаров с использованием современных технологий машинного обучения и обработки данных. 