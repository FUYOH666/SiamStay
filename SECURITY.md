# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Best Practices

### Secrets Management

- **Never commit secrets** to the repository
- All secrets must be stored in `.env` file (not in `config.yaml`)
- `.env` file is in `.gitignore` and should never be committed
- Use strong encryption keys for TM30 credentials

### TM30 Credentials

- TM30 credentials are encrypted using Fernet (symmetric encryption)
- Encryption key (`TM30_ENCRYPTION_KEY`) must be 32-byte base64-encoded
- Generate encryption key using:
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- Encryption key must be kept secure and never shared

### Database Security

- Use strong PostgreSQL passwords
- Restrict database access to application servers only
- Use SSL/TLS for database connections in production

### API Security

- Implement authentication and authorization (TODO)
- Use HTTPS in production
- Validate all input data
- Implement rate limiting

### Reporting a Vulnerability

If you discover a security vulnerability, please report it to:

- **Email**: @scanovich_ai
- **GitHub**: Create a private security advisory

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

We will acknowledge receipt within 48 hours and provide updates on the investigation and fix.
