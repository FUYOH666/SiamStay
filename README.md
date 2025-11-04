# 🏡 SiamStay

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![Thailand](https://img.shields.io/badge/Market-Thailand-green.svg)](https://github.com/FUYOH666/SiamStay)

<div align="center">

**🌍 Language:** [🇷🇺 Русский (Main)](README.md) | [🇺🇸 English](README_EN.md) | [🇹🇭 ไทย](README_TH.md)

</div>

**Platform for villa rental management in Thailand with automatic TM30 registration.**

SiamStay - это комплексная платформа для управления арендой вилл в Таиланде (30+ дней) с автоматической регистрацией гостей через TM30 API.

---

## Краткое описание

SiamStay автоматизирует весь цикл аренды вилл:
- **Управление виллами** - создание, валидация, compliance проверки
- **Бронирование** - онлайн-бронирование с автоматическим расчетом цен
- **Автоматическая TM30 регистрация** - регистрация гостей через TM30 API без участия владельца
- **Платежи** - интеграция с платежными системами
- **Уведомления** - автоматические напоминания для гостей и владельцев

---

## Требования

- **Python 3.12** - единственная поддерживаемая версия
- **PostgreSQL 14+** - база данных
- **Redis 6+** - кэширование и очереди
- **uv** - менеджер пакетов (устанавливается автоматически)

---

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/FUYOH666/SiamStay.git
cd SiamStay
```

### 2. Установка зависимостей

```bash
# Установка uv (если еще не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей проекта
uv sync
```

### 3. Настройка конфигурации

```bash
# Копировать пример .env файла
cp .env.example .env

# Отредактировать .env файл и заполнить необходимые значения
# ⭐️ Критично: DATABASE_URL, REDIS_URL, TM30_ENCRYPTION_KEY (если TM30 включен)
```

### 4. Настройка базы данных

```bash
# Создать базу данных PostgreSQL
createdb siamstay

# Запустить миграции
uv run alembic upgrade head
```

---

## Конфигурация

### Основные настройки (config.yaml)

Основные настройки находятся в `config.yaml`. Секреты и переопределения - через переменные окружения в `.env`.

### Переменные окружения (.env)

**Обязательные:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Для TM30 интеграции:**
- `TM30_ENABLED=true` - включить TM30 интеграцию
- `TM30_ENCRYPTION_KEY` - ключ шифрования для TM30 credentials (32-byte base64)

**Для платежей:**
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLIC_KEY` - Stripe public key

**Для уведомлений:**
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - настройки SMTP

### Генерация TM30 encryption key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Полученный ключ добавить в `.env` как `TM30_ENCRYPTION_KEY`.

---

## Запуск

### Разработка

```bash
# Запуск FastAPI сервера
uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Использование gunicorn
uv run gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```bash
# Сборка образа
docker build -t siamstay .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env siamstay
```

---

## API документация

После запуска приложения:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/healthz
- **Metrics**: http://localhost:8000/metrics

---

## Основные endpoints

### Properties (Виллы)

- `POST /properties` - создать виллу
- `GET /properties/{id}` - получить виллу
- `GET /properties/{id}/availability` - проверить доступность
- `GET /properties/{id}/price` - рассчитать цену
- `POST /properties/{id}/validate-compliance` - валидация compliance

### Bookings (Бронирования)

- `POST /bookings` - создать бронирование
- `GET /bookings/{id}` - получить бронирование
- `POST /bookings/{id}/confirm` - подтвердить бронирование
- `POST /bookings/{id}/check-in` - заселение гостя

### TM30

- `POST /tm30/bookings/{id}/register` - зарегистрировать гостя через TM30
- `GET /tm30/bookings/{id}/status` - получить статус TM30 регистрации

---

## TM30 интеграция

### Настройка TM30 credentials для владельца

1. Владелец предоставляет логин и пароль для TM30 системы
2. Credentials шифруются и сохраняются в базе данных
3. При check-in гостя автоматически происходит регистрация через TM30 API

### Отключение TM30 интеграции

Если TM30 интеграция не нужна, установить в `config.yaml`:

```yaml
tm30:
  enabled: false
```

---

## Приёмка

### Проверка работоспособности

1. **Health check:**
   ```bash
   curl http://localhost:8000/healthz
   ```

2. **Создание виллы:**
   ```bash
   curl -X POST http://localhost:8000/properties \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Villa", "address": "123 Test St", ...}'
   ```

3. **Проверка доступности:**
   ```bash
   curl "http://localhost:8000/properties/1/availability?check_in=2025-01-01&check_out=2025-02-01"
   ```

---

## Тестирование

```bash
# Запуск всех тестов
uv run pytest

# Запуск с покрытием
uv run pytest --cov=app --cov-report=html

# Запуск конкретного теста
uv run pytest tests/test_properties.py
```

---

## Структура проекта

```
Siamstay/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Бизнес-логика
│   ├── integrations/      # Внешние интеграции (TM30, payments)
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Сервисы (notifications, encryption)
│   ├── db/               # База данных
│   └── utils/            # Утилиты
├── tests/                # Тесты
├── alembic/              # Миграции БД
├── config.yaml           # Конфигурация
├── pyproject.toml        # Зависимости
└── README.md            # Документация
```

---

## Частые ошибки

### Ошибка: "TM30_ENCRYPTION_KEY must be set"

**Решение:** Генерировать ключ и добавить в `.env`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Ошибка: "Database connection failed"

**Решение:** Проверить `DATABASE_URL` в `.env` и что PostgreSQL запущен.

### Ошибка: "Minimum stay is 30 days"

**Решение:** Это требование тайского законодательства. Бронирования должны быть минимум 30 дней.

---

## Разработка

### Добавление новой зависимости

```bash
uv add package-name
```

### Создание миграции БД

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

### Линтинг и форматирование

```bash
uv run ruff check .
uv run ruff format .
```

---

## Лицензия

MIT License

---

## Контакты

**Автор:** Aleksandr Mordvinov

- **Email**: @scanovich_ai
- **GitHub**: [FUYOH666](https://github.com/FUYOH666)

---

**💡 SiamStay - автоматизация аренды вилл в Таиланде с автоматической TM30 регистрацией.**
