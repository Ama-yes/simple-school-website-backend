# School Management Backend API
A simple yet scalable backend API for managing students, built with FASTAPI, SQLAlchemy and PostreSQL.


## Features
- Distinct and clean architecture.
- Authentification system with token refresh feature.
- Secure password hashing.
- Strict user input validation.


## Stack
- Language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL and ORM with SQLAlchemy
- Package manager using `uv`


## Project Structure
```
app/
├── api
│   └── v1
├── core
├── db
├── models
├── repositories

└── main.py
```


## Getting Started
### 1. Prerequisites
- Python 3.11+ installed.
- [uv](https://github.com/astral-sh/uv) installed.

### 2. Environment Setup
Create `example.env` to `.env` and fill in the fields

### 3. Installation
Install dependencies using `uv`:
uv sync

### 4. Running the API Server
Run the server using:
uv run python3 -m app.main


## Authentication Flow
1. **Signin or Login:** Students send their credentials to '/student/signin' to sign up (or '/student/login' to login), admins send their credentials to '/admin/signin' to sign up (or '/admin/login' to login).
2. **Response:** The server returns an 'access_token' (short-lived) and a 'refresh_token' (long-lived).
3. **Access:** Use the 'access_token' in the 'Authorization: Bearer <token>' header for protected routes.
4. **Refresh:** When 'access_token' expires, send 'refresh_token' in the 'Authorization: Bearer <token>' header to '/student/refresh' for students or '/admin/refresh' for admins to generate a new one.
5. **Revocation:** Changing the password instantly invalidates previously created tokens.
