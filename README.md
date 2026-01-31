# High-Performance School Management API (WORK IN PROGRESS)
A fully asynchronous, performant and scalable backend API, built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**.


## Features
- Fully Asynchronous and optimized for high concurrency using 'asyncpg' for non-blocking database I/O.
- Redis Integration:
    - Asynchronous caching to reduce database pressure.
    - Rate limiting to protect the system from brute-force attacks.
- Security:
    - Token versioning allows session revocation upon password change.
    - Secure password hashing.
    - Authentication system with token refresh feature.
    - Strict user input validation.
- Clean and clear separation between API controllers, data repositories and core logic.
- Automated orchestration and deployment via docker and with separate database initialization.


## Stack
- Language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL via SQLAlchemy 2.0 using 'asyncpg' driver.
- Redis.
- Package manager using `uv`


## Project Structure
```
├── app
│   ├── api
│   │   └── v1
│   ├── core
│   ├── db
│   ├── models
│   ├── repositories
│   ├── worker
│   └── main.py
└── tests
```


## Getting Started
### 1. Environment Configuration
Rename the `example.env` to `.env` and fill in the required fields.
(Note: If the SMTP fields are left empty, emails will be sent to mailpit)

### 2. Launch the Stack
Run the entire environment using:
`docker compose up --build -d`
(Note: `init_db` will handle schema creation automatically on startup)

### 3. Access Documentation
Once running, visit:
- Interactive Swagger Docs: `http://localhost:8000/docs`
- Mailpit (Local email testing): `http://localhost:8025`

## Testing & Verification
The project includes comprehensive asynchronous testing using `pytest` and `pytest-asyncio`.

**Run the tests:**
`uv run python -m pytest`

*Although the test suite uses an isolated in-memory SQLite database, it still requires a redis instance to be running to handle caching behavior*


## Authentication Flow
1. **Signin or Login:** Students send their credentials to '/student/signin' to sign up (or '/student/login' to login), admins send their credentials to '/admin/signin' to sign up (or '/admin/login' to login).
2. **Response:** The server returns an 'access_token' (short-lived) and a 'refresh_token' (long-lived).
3. **Access:** Use the 'access_token' in the 'Authorization: Bearer <token>' header for protected routes.
4. **Refresh:** When 'access_token' expires, send 'refresh_token' in the 'Authorization: Bearer <token>' header to '/student/refresh' for students or '/admin/refresh' for admins to generate a new one.
5. **Revocation:** Changing the password instantly invalidates previously created tokens.
