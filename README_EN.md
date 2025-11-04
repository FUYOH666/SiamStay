# 🏡 SiamStay

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)

<div align="center">

**🌍 Language:** [🇷🇺 Русский (Main)](README.md) | [🇺🇸 English](README_EN.md) | [🇹🇭 ไทย](README_TH.md)

</div>

---

**Platform for villa rental management in Thailand with automatic TM30 registration.**

SiamStay automates the entire villa rental cycle:
- **Villa Management** - Create, validate, and manage villa properties
- **Online Booking** - Automatic pricing and availability checks
- **Automatic TM30 Registration** - Register guests via TM30 API without owner involvement
- **Payments** - Payment processing integration
- **Notifications** - Automated reminders for guests and owners

---

## Features

- ✅ **Villa-focused** - Simplified property management for villas only
- ✅ **TM30 Integration** - Automatic guest registration with Thai Immigration
- ✅ **30+ Days Minimum** - Full compliance with Thai rental regulations
- ✅ **Modern Stack** - Python 3.12, FastAPI, PostgreSQL, Redis
- ✅ **Encrypted Credentials** - Secure storage of TM30 owner credentials
- ✅ **Health Monitoring** - Health checks and Prometheus metrics
- ✅ **API-First** - RESTful API with OpenAPI documentation

---

## Requirements

- **Python 3.12** - Single supported version
- **PostgreSQL 14+** - Database
- **Redis 6+** - Caching and queues
- **uv** - Package manager (installed automatically)

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/FUYOH666/SiamStay.git
cd SiamStay
```

### 2. Install Dependencies

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Configuration

```bash
# Copy example .env file
cp .env.example .env

# Edit .env file and fill in required values
# ⭐️ Critical: DATABASE_URL, REDIS_URL, TM30_ENCRYPTION_KEY (if TM30 enabled)
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb siamstay

# Run migrations
uv run alembic upgrade head
```

---

## Configuration

### Main Settings (config.yaml)

Main settings are in `config.yaml`. Secrets and overrides via environment variables in `.env`.

### Environment Variables (.env)

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**For TM30 Integration:**
- `TM30_ENABLED=true` - Enable TM30 integration
- `TM30_ENCRYPTION_KEY` - Encryption key for TM30 credentials (32-byte base64)

**For Payments:**
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_PUBLIC_KEY` - Stripe public key

**For Notifications:**
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - SMTP settings

### Generate TM30 Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated key to `.env` as `TM30_ENCRYPTION_KEY`.

---

## Running

### Development

```bash
# Run FastAPI server
uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# Using gunicorn
uv run gunicorn app.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```bash
# Build image
docker build -t siamstay .

# Run container
docker run -p 8000:8000 --env-file .env siamstay
```

---

## API Documentation

After starting the application:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/healthz
- **Metrics**: http://localhost:8000/metrics

---

## Main Endpoints

### Properties (Villas)

- `POST /properties` - Create villa
- `GET /properties/{id}` - Get villa
- `GET /properties/{id}/availability` - Check availability
- `GET /properties/{id}/price` - Calculate price
- `POST /properties/{id}/validate-compliance` - Validate compliance

### Bookings

- `POST /bookings` - Create booking
- `GET /bookings/{id}` - Get booking
- `POST /bookings/{id}/confirm` - Confirm booking
- `POST /bookings/{id}/check-in` - Check in guest

### TM30

- `POST /tm30/bookings/{id}/register` - Register guest via TM30
- `GET /tm30/bookings/{id}/status` - Get TM30 registration status

---

## TM30 Integration

### Setup TM30 Credentials for Owner

1. Owner provides login and password for TM30 system
2. Credentials are encrypted and stored in database
3. Automatic registration occurs via TM30 API when guest checks in

### Disable TM30 Integration

If TM30 integration is not needed, set in `config.yaml`:

```yaml
tm30:
  enabled: false
```

---

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/test_properties.py
```

---

## Project Structure

```
Siamstay/
├── app/
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Business logic
│   ├── integrations/      # External integrations (TM30, payments)
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Services (notifications, encryption)
│   ├── db/               # Database
│   └── utils/            # Utilities
├── tests/                # Tests
├── alembic/              # Database migrations
├── config.yaml           # Configuration
├── pyproject.toml        # Dependencies
└── README.md            # Documentation
```

---

## Common Issues

### Error: "TM30_ENCRYPTION_KEY must be set"

**Solution:** Generate key and add to `.env`:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Error: "Database connection failed"

**Solution:** Check `DATABASE_URL` in `.env` and ensure PostgreSQL is running.

### Error: "Minimum stay is 30 days"

**Solution:** This is a Thai legal requirement. Bookings must be minimum 30 days.

---

## Development

### Adding New Dependency

```bash
uv add package-name
```

### Creating Database Migration

```bash
uv run alembic revision --autogenerate -m "description"
uv run alembic upgrade head
```

### Linting and Formatting

```bash
uv run ruff check .
uv run ruff format .
```

---

## License

MIT License

---

## Contact

**Author:** Aleksandr Mordvinov

- **Email**: @scanovich_ai
- **GitHub**: [FUYOH666](https://github.com/FUYOH666)

---

**💡 SiamStay - Villa rental automation in Thailand with automatic TM30 registration.**
