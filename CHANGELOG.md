# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-11-04

### Added

- Initial project structure with Python 3.12 + uv
- FastAPI application with async support
- PostgreSQL database models (Property, Owner, Guest, Booking, Payment, TM30Registration)
- Property management service (villa-only, simplified)
- Booking management service with 30+ days minimum stay validation
- TM30 API integration with automatic guest registration
- TM30 credentials encryption service
- Health check endpoint (`/healthz`)
- Prometheus metrics endpoint (`/metrics`)
- API endpoints for properties, bookings, and TM30
- Configuration management with pydantic-settings (YAML + ENV)
- Alembic migrations setup
- Basic tests (config, properties, bookings)
- Documentation (README, CHANGELOG)

### Changed

- Complete refactoring from old structure to modern Python 3.12 + uv stack
- Simplified property model to focus on villas only
- Removed condo-specific logic and fields

### Security

- TM30 credentials encrypted using Fernet (cryptography)
- Environment variables for all secrets
- Fail-fast validation for critical settings

[0.1.0]: https://github.com/FUYOH666/SiamStay/releases/tag/v0.1.0
