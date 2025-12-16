# Apex SaaS Framework

A pure Python SDK for multi-tenant SaaS applications. Database-agnostic and framework-agnostic.

## Features

- **Authentication**: Signup, login, JWT tokens, password reset
- **Users**: User management with flexible models
- **Organizations**: Multi-tenant organization support
- **RBAC**: Roles and permissions system
- **Payments**: PayPal integration
- **Email**: SendGrid integration
- **Files**: File upload and management
- **Settings**: Application settings management

## Quick Start

```python
from apex import Client, set_default_client, bootstrap
from apex.auth import signup, login
from apex.core.base import Base, UUIDPKMixin, TimestampMixin
from sqlalchemy import Column, String

# Define your models
class User(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "users"
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))

# Initialize client
client = Client(database_url="sqlite+aiosqlite:///./mydb.db", user_model=User)
set_default_client(client)

# Bootstrap database
bootstrap(models=[User])

# Use functions directly
user = signup(email="user@example.com", password="pass123")
tokens = login(email="user@example.com", password="pass123")
```

## Installation

```bash
pip install apex-saas-framework
```

## Documentation

For detailed documentation, visit: https://github.com/apexneural/apex-saas-framework

## License

MIT License
