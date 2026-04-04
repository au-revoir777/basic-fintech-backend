# zorvyn-deploy

[![Build Status](https://img.shields.io/travis/au-revoir777/zorvyn-deploy.svg?style=flat-square)](https://travis-ci.org/au-revoir777/zorvyn-deploy)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

This repository contains the backend API for the Zorvyn financial dashboard, built with FastAPI. It provides a secure, scalable, and production-ready foundation for financial data management and analysis.

## Features

*   **FastAPI Framework:** Leverages the high-performance FastAPI framework for building robust APIs.
*   **JWT Authentication:** Implements JSON Web Token (JWT) based authentication for secure access.
*   **Role-Based Access Control (RBAC):** Enforces granular access permissions based on user roles.
*   **Financial Record Management:** Comprehensive API endpoints for creating, reading, updating, and deleting financial records.
*   **Database Migrations:** Utilizes Alembic for managing database schema evolution.
*   **Environment Variable Configuration:** Supports configuration through environment variables for flexible deployment.
*   **Rate Limiting:** Implements rate limiting to protect the API from abuse.

## Installation

### Prerequisites

*   Python 3.9+
*   pip (Python package installer)

### Cloning the Repository

```bash
git clone https://github.com/au-revoir777/zorvyn-deploy.git
cd zorvyn-deploy
```

### Setting up the Environment

1.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

2.  **Activate the virtual environment:**

    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install project dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Copy the example environment file and populate it with your specific settings.

    ```bash
    cp .env.example .env
    ```

    Edit the `.env` file and set the following variables:
    *   `DATABASE_URL`: Your database connection string (e.g., `postgresql://user:password@host:port/database`).
    *   `SECRET_KEY`: A strong, secret key for JWT signing.
    *   `ALGORITHM`: The JWT signing algorithm (e.g., `HS256`).
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for access tokens in minutes.
    *   `REFRESH_TOKEN_EXPIRE_MINUTES`: The expiration time for refresh tokens in minutes.
    *   `REDIS_HOST`: Redis host if used for caching or token blocklisting.
    *   `REDIS_PORT`: Redis port if used.

### Database Migrations

Apply the database migrations to set up your database schema.

```bash
alembic upgrade head
```

### Running the Development Server

```bash
uvicorn app.main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

## Usage

### API Documentation

The API documentation is automatically generated and available at the `/docs` endpoint when the server is running.

Access the interactive API documentation here: [https://zorvyn-deploy.vercel.app/docs](https://zorvyn-deploy.vercel.app/docs)

### Example API Calls

**1. User Registration (POST /api/v1/users/register)**

```bash
curl -X POST "https://zorvyn-deploy.vercel.app/api/v1/users/register" \
-H "Content-Type: application/json" \
-d '{
  "email": "testuser@example.com",
  "password": "securepassword123",
  "full_name": "Test User"
}'
```

**2. User Login (POST /api/v1/auth/login)**

```bash
curl -X POST "https://zorvyn-deploy.vercel.app/api/v1/auth/login" \
-H "Content-Type: application/json" \
-d '{
  "username": "testuser@example.com",
  "password": "securepassword123"
}'
```

This will return an access token and a refresh token.

**3. Create Financial Record (POST /api/v1/records)**
Requires authentication. Include the access token in the `Authorization` header as a Bearer token.

```bash
curl -X POST "https://zorvyn-deploy.vercel.app/api/v1/records" \
-H "Content-Type: application/json" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
-d '{
  "title": "Monthly Salary",
  "amount": 5000.00,
  "type": "income",
  "category": "salary",
  "date": "2023-10-27T10:00:00Z"
}'
```

**4. Get Financial Records (GET /api/v1/records)**
Requires authentication.

```bash
curl -X GET "https://zorvyn-deploy.vercel.app/api/v1/records" \
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration

The application's configuration is managed through environment variables. The following variables are essential for running the application:

| Variable Name                 | Description                                                              | Default Value |
| :---------------------------- | :----------------------------------------------------------------------- | :------------ |
| `DATABASE_URL`                | PostgreSQL connection URL.                                               | None          |
| `SECRET_KEY`                  | Secret key for signing JWTs.                                             | None          |
| `ALGORITHM`                   | JWT signing algorithm.                                                   | `HS256`       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiration time for access tokens in minutes.                            | `30`          |
| `REFRESH_TOKEN_EXPIRE_MINUTES`| Expiration time for refresh tokens in minutes.                           | `720`         |
| `REDIS_HOST`                  | Hostname for the Redis server (if used).                                 | `localhost`   |
| `REDIS_PORT`                  | Port for the Redis server (if used).                                     | `6379`        |
| `ITEMS_PER_PAGE`              | Default number of items to return per paginated request.                 | `50`          |
| `API_V1_STR`                  | Base path for API version 1.                                             | `/api/v1`     |

## API Endpoints

The API follows a RESTful architecture. Key endpoints include:

*   **Authentication (`/api/v1/auth`)**
    *   `POST /login`: Authenticate a user and receive JWT tokens.
    *   `POST /login/access-token`: Obtain a new access token using a refresh token.
    *   `POST /refresh-token`: Obtain a new refresh token.
    *   `POST /test-token`: Test the validity of a token.
*   **Users (`/api/v1/users`)**
    *   `POST /register`: Register a new user.
    *   `GET /me`: Retrieve the currently authenticated user's information.
    *   `PUT /me`: Update the currently authenticated user's information.
*   **Financial Records (`/api/v1/records`)**
    *   `POST /`: Create a new financial record.
    *   `GET /`: Retrieve a list of financial records, with support for filtering and pagination.
    *   `GET /{id}`: Retrieve a specific financial record by its ID.
    *   `PUT /{id}`: Update a specific financial record by its ID.
    *   `DELETE /{id}`: Delete a specific financial record by its ID.
*   **Dashboard (`/api/v1/dashboard`)**
    *   `GET /summary`: Retrieve a summary of financial data for the dashboard.

Detailed endpoint specifications, request/response schemas, and parameters can be found in the [API Documentation](https://zorvyn-deploy.vercel.app/docs).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <a href="https://readmeforge.app?utm_source=badge">
    <img src="https://readmeforge.app/badge.svg" alt="Made with ReadmeForge" height="20">
  </a>
</p>