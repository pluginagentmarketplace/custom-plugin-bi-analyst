# Backend Development Guide

> BI Analyst Plugin - Backend Skill Reference
> Version: 1.0.0

## Overview

This guide covers modern backend development patterns with focus on FastAPI, but principles apply to Django, Flask, Express, and other frameworks. Emphasis on scalable, secure, and maintainable API design.

## Table of Contents

1. [API Design Principles](#api-design-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [Database Patterns](#database-patterns)
4. [Error Handling](#error-handling)
5. [Testing Strategies](#testing-strategies)
6. [Performance Optimization](#performance-optimization)

---

## API Design Principles

### RESTful Design Guidelines

| HTTP Method | Purpose | Idempotent | Safe |
|------------|---------|------------|------|
| GET | Retrieve resources | Yes | Yes |
| POST | Create resources | No | No |
| PUT | Replace resources | Yes | No |
| PATCH | Partial update | Yes | No |
| DELETE | Remove resources | Yes | No |

### URL Design Best Practices

```python
# ✅ GOOD - Nouns, plural, hierarchical
GET    /api/v1/users                    # List users
GET    /api/v1/users/{id}               # Get user
POST   /api/v1/users                    # Create user
PUT    /api/v1/users/{id}               # Replace user
PATCH  /api/v1/users/{id}               # Update user
DELETE /api/v1/users/{id}               # Delete user
GET    /api/v1/users/{id}/orders        # User's orders
GET    /api/v1/users/{id}/orders/{oid}  # Specific order

# ❌ BAD - Verbs, inconsistent
GET    /api/getUsers
POST   /api/createUser
GET    /api/user/delete/{id}
```

### FastAPI Endpoint Pattern

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all users with pagination.

    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return (max 100)
    """
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Create a new user (admin only)."""
    service = UserService(db)

    if service.get_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return service.create(user_data)
```

---

## Authentication & Authorization

### JWT Authentication Flow

```
┌──────────┐    credentials    ┌──────────┐
│  Client  │ ───────────────→  │  Server  │
└──────────┘                   └──────────┘
                                    │
                               ┌────▼────┐
                               │ Validate │
                               │ Creds    │
                               └────┬────┘
                                    │
┌──────────┐    access_token   ┌────▼────┐
│  Client  │ ←───────────────  │ Generate │
└──────────┘   refresh_token   │ Tokens   │
     │                         └──────────┘
     │ access_token
     ▼
┌──────────┐                   ┌──────────┐
│ Request  │ ───────────────→  │ Verify   │
│ + Token  │                   │ Token    │
└──────────┘                   └──────────┘
```

### JWT Implementation

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Configuration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


# Role-based access control
def require_role(required_roles: list[str]):
    """Dependency factory for role-based access."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Usage
@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(["admin", "superadmin"])),
):
    """Delete user (admin only)."""
    ...
```

---

## Database Patterns

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Abstract base repository with CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User-specific repository with custom queries."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_active_users(self) -> list[User]:
        return self.db.query(User).filter(User.is_active == True).all()
```

### Database Migrations with Alembic

```bash
# Initialize alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## Error Handling

### Standardized Error Response

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str
    message: str
    details: dict | None = None
    request_id: str | None = None


class AppException(Exception):
    """Base application exception."""
    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: dict | None = None
    ):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.details = details


class NotFoundError(AppException):
    def __init__(self, resource: str, id: any):
        super().__init__(
            status_code=404,
            error="NOT_FOUND",
            message=f"{resource} with id {id} not found"
        )


class ValidationError(AppException):
    def __init__(self, details: dict):
        super().__init__(
            status_code=422,
            error="VALIDATION_ERROR",
            message="Request validation failed",
            details=details
        )


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error,
            message=exc.message,
            details=exc.details,
            request_id=request.state.request_id
        ).model_dump()
    )


# Usage in endpoints
@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User", user_id)
    return user
```

---

## Testing Strategies

### Test Structure

```
tests/
├── conftest.py          # Fixtures
├── unit/                # Unit tests
│   ├── test_services.py
│   └── test_utils.py
├── integration/         # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── e2e/                 # End-to-end tests
    └── test_workflows.py
```

### Pytest Fixtures

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.deps import get_db
from app.db.base import Base

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for test user."""
    response = client.post("/auth/token", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

### API Tests

```python
# test_api.py
class TestUserAPI:
    def test_create_user(self, client, auth_headers):
        response = client.post(
            "/api/v1/users",
            headers=auth_headers,
            json={
                "email": "new@example.com",
                "password": "secure123!",
                "name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert "password" not in data

    def test_create_user_duplicate_email(self, client, auth_headers):
        # Create first user
        client.post("/api/v1/users", headers=auth_headers, json={
            "email": "dup@example.com", "password": "pass123!", "name": "User"
        })

        # Try duplicate
        response = client.post("/api/v1/users", headers=auth_headers, json={
            "email": "dup@example.com", "password": "pass123!", "name": "User 2"
        })
        assert response.status_code == 409
        assert response.json()["error"] == "CONFLICT"
```

---

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
from redis import Redis
import json

redis_client = Redis.from_url(settings.REDIS_URL)


def cache_response(key_prefix: str, ttl: int = 3600):
    """Decorator for caching endpoint responses."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"

            # Try cache first
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator


# Usage
@router.get("/stats")
@cache_response("stats", ttl=300)  # 5 minutes
async def get_stats():
    return {"users": 1000, "orders": 5000}
```

### Database Query Optimization

```python
# ✅ GOOD - Eager loading to prevent N+1
def get_users_with_orders(db: Session) -> list[User]:
    return db.query(User).options(
        joinedload(User.orders)
    ).all()


# ✅ GOOD - Pagination with total count
def get_paginated_users(db: Session, page: int, size: int) -> dict:
    query = db.query(User)
    total = query.count()
    users = query.offset((page - 1) * size).limit(size).all()

    return {
        "items": users,
        "total": total,
        "page": page,
        "pages": (total + size - 1) // size
    }


# ❌ BAD - N+1 query problem
def get_users_bad(db: Session):
    users = db.query(User).all()
    for user in users:
        # This triggers a query for each user!
        orders = user.orders
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org)
- [Alembic Migrations](https://alembic.sqlalchemy.org)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [12-Factor App](https://12factor.net)

---

*Last Updated: 2025-01-01*
*BI Analyst Plugin - Backend Skill*
