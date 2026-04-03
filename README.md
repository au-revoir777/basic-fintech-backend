# Finance Dashboard Backend API

A secure, scalable, and production-ready backend API for a financial dashboard built with FastAPI. Features JWT authentication, role-based access control (RBAC), comprehensive financial record management, and real-time analytics.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens)](https://jwt.io/)

## Features

### Core Functionality

- **User Management**: Complete CRUD operations for users with role-based permissions
- **Financial Records**: Full CRUD for income/expense tracking with advanced filtering
- **Dashboard Analytics**: Real-time summaries, trends, and category breakdowns
- **Authentication**: JWT-based auth with access/refresh token rotation
- **Authorization**: Role-based access control (Viewer, Analyst, Admin)

### Security & Performance

- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options
- **Rate Limiting**: Configurable per-minute request limits
- **Account Protection**: Login attempt tracking and temporary lockouts
- **Token Revocation**: Secure logout with refresh token blacklisting
- **Input Validation**: Comprehensive Pydantic validation with detailed error messages
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM

### Developer Experience

- **Auto-generated API Docs**: Interactive Swagger UI at `/docs`
- **Hot Reload**: Development server with automatic code reloading
- **Database Migrations**: Alembic for schema versioning and updates
- **Type Safety**: Full type hints throughout the codebase
- **Clean Architecture**: Repository → Service → API layer separation

## Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- **Database**: SQLite (development) / PostgreSQL (production)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.com/) - Database migration tool
- **Authentication**: [PyJWT](https://pyjwt.readthedocs.io/) - JSON Web Tokens
- **Password Hashing**: [Passlib](https://passlib.readthedocs.io/) - Secure password hashing
- **Validation**: [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- Virtual environment support (venv)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd assignment-zorvyn

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional - defaults work for development)
# nano .env  # or your preferred editor
```

### 4. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Optional: Create initial admin user
python create_admin.py
```

### 5. Start Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload

# Or specify host/port
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`

## API Documentation

### Interactive Documentation

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

### API Endpoints Overview

| Endpoint                    | Method       | Description           | Access        |
| --------------------------- | ------------ | --------------------- | ------------- |
| `/health`                   | GET          | Health check          | Public        |
| `/api/v1/auth/login`        | POST         | User authentication   | Public        |
| `/api/v1/auth/refresh`      | POST         | Refresh access token  | Authenticated |
| `/api/v1/auth/logout`       | POST         | Logout user           | Authenticated |
| `/api/v1/users`             | GET/POST     | List/Create users     | Admin         |
| `/api/v1/users/{id}`        | PATCH        | Update user           | Admin         |
| `/api/v1/records`           | GET/POST     | List/Create records   | Viewer+       |
| `/api/v1/records/{id}`      | PATCH/DELETE | Update/Delete record  | Analyst+      |
| `/api/v1/dashboard/summary` | GET          | Financial summary     | Viewer+       |
| `/api/v1/dashboard/trends`  | GET          | Income/expense trends | Viewer+       |
| `/api/v1/dashboard/recent`  | GET          | Recent transactions   | Viewer+       |

## Authentication & Authorization

### Authentication Flow

1. **Login** with email/password to receive JWT tokens
2. **Use access token** in `Authorization: Bearer <token>` header
3. **Refresh tokens** when access token expires
4. **Logout** to revoke refresh token

### Example Login Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Role-Based Permissions

| Role        | Description          | Permissions                           |
| ----------- | -------------------- | ------------------------------------- |
| **Viewer**  | Read-only access     | View records, dashboard analytics     |
| **Analyst** | Data analyst         | All viewer permissions + CRUD records |
| **Admin**   | System administrator | All permissions + user management     |

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'viewer',
    is_active BOOLEAN NOT NULL DEFAULT 1,
    failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until DATETIME,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### Financial Records Table

```sql
CREATE TABLE financial_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(12,2) NOT NULL,
    record_type VARCHAR(20) NOT NULL,
    category VARCHAR(120) NOT NULL,
    record_date DATE NOT NULL,
    notes TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### Token Blocklist Table

```sql
CREATE TABLE token_blocklist (
    jti VARCHAR(255) PRIMARY KEY,
    token_type VARCHAR(20) NOT NULL,
    expires_at DATETIME NOT NULL
);
```

## Configuration

### Environment Variables

| Variable                      | Default                | Description                |
| ----------------------------- | ---------------------- | -------------------------- |
| `APP_NAME`                    | Finance Dashboard API  | Application name           |
| `API_V1_PREFIX`               | /api/v1                | API version prefix         |
| `DATABASE_URL`                | sqlite:///./finance.db | Database connection URL    |
| `JWT_SECRET_KEY`              | (required)             | Secret key for JWT signing |
| `JWT_ALGORITHM`               | HS256                  | JWT algorithm              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 15                     | Access token lifetime      |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | 7                      | Refresh token lifetime     |
| `CORS_ORIGINS`                | http://localhost:3000  | Allowed CORS origins       |
| `RATE_LIMIT_PER_MINUTE`       | 120                    | Requests per minute limit  |
| `LOGIN_MAX_ATTEMPTS`          | 5                      | Max failed login attempts  |
| `LOGIN_LOCKOUT_MINUTES`       | 15                     | Account lockout duration   |

### Database Migration

```bash
# Create new migration
alembic revision --autogenerate -m "migration description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Testing

### Run Health Check

```bash
curl http://127.0.0.1:8000/health
# Expected: {"status": "ok"}
```

### Run Existing Tests

```bash
pytest tests/
```

### Manual Testing with Swagger UI

1. Visit `http://127.0.0.1:8000/docs`
2. Use "Try it out" buttons on endpoints
3. Authenticate using the login endpoint first

## Deployment

### Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL

   ```bash
   export DATABASE_URL="postgresql://user:pass@localhost/dbname"
   ```

2. **Security**: Change JWT secret key

   ```bash
   export JWT_SECRET_KEY="your-secure-random-key-here"
   ```

3. **HTTPS**: Enable SSL/TLS in production
4. **Environment**: Set `ENV=production` for optimizations

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN alembic upgrade head

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Project Structure

```
assignment-zorvyn/
├── alembic/                 # Database migrations
│   ├── versions/           # Migration files
│   └── env.py             # Migration environment
├── app/                    # Application code
│   ├── api/               # API routes
│   │   └── v1/           # API v1 endpoints
│   ├── core/             # Core functionality
│   │   ├── config.py     # Configuration
│   │   ├── deps.py       # Dependencies
│   │   └── security.py   # Security utilities
│   ├── db/               # Database setup
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── tests/                 # Test files
├── .env.example          # Environment template
├── alembic.ini           # Alembic configuration
├── create_admin.py       # Admin user creation script
├── main.py              # Application entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to new functions
- Write tests for new features
- Update documentation as needed
- Use meaningful commit messages

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - The modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Alembic](https://alembic.sqlalchemy.com/) - Database migration tool
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation

## Support

If you have any questions or issues:

1. Check the [API Documentation](http://127.0.0.1:8000/docs)
2. Review the [Issues](../../issues) page
3. Create a new issue with detailed information

---

**Happy coding!**

- **analyst**: viewer + create/update records
- **admin**: analyst + delete records + user management

## Notes / Trade-offs

- Rate limiting uses in-memory storage (suitable for single process dev). Replace with Redis for multi-instance production.
- HTTPS enforcement is expected at reverse proxy/load balancer level; app includes proxy-aware security headers.
