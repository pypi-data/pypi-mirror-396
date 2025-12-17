# AuthCore — Multi-Framework Authentication

`authcore` is a unified authentication and authorization library for **FastAPI**, **Flask**, and **Django**, designed to simplify secure login, session, and OAuth2 handling.

It supports:
- **JWT-based authentication**
- **Session-based authentication**
- **OAuth2 logins** (Google, GitHub, etc.)
- **Two-Factor Authentication (2FA)**
- **RBAC (Role-Based Access Control)**

---

## Table of Contents

- [Common Components](#-common-components)
- [FastAPI Integration](#-fastapi-integration)
- [Flask Integration](#-flask-integration)
- [Django Integration](#-django-integration)
- [Supported Authentication Modes](#-supported-authentication-modes)
- [RBAC Example](#-rbac-role-based-access-control)
- [Two-Factor Authentication (2FA)](#-2fa-example)
- [Summary Table](#-summary)

---

## ⚙️ Common Components

All frameworks share the same core configuration system.

| Component | Purpose |
|------------|----------|
| **AuthCoreConfig** | Central configuration combining JWT, session, and OAuth settings. |
| **JwtConfig** | Defines JWT signing secret, expiry, and refresh rules. |
| **SessionConfig** | Controls server-side session authentication. |
| **OAuth2Config / OAuthProviderConfig** | Manages OAuth2 login flows for providers like Google or GitHub. |
| **TwoFAConfig** | Enables OTP-based two-factor authentication. |
| **UserRepository** | Abstract interface you implement to connect to your user database. |

---

## 🚀 FastAPI Integration

### Example: `main.py`

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from authcore import (
    FastAPIAuthCore, AuthCoreConfig, JwtConfig, SessionConfig,
    EndpointEnabled, UserRepository, require_permission
)
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Database Setup ---
engine = create_engine("sqlite:///./test.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="ROLE_USER")

Base.metadata.create_all(bind=engine)

# --- Repository Implementation ---
class UserRepositoryImpl(UserRepository):
    def __init__(self):
        self.db = SessionLocal()
    async def get_by_email(self, email: str):
        user = self.db.query(UserORM).filter(UserORM.email == email).first()
        if not user:
            return None
        return {"id": user.id, "email": user.email, "password": user.password, "roles": [user.role]}
    async def verify_password(self, plain: str, phash: str) -> bool:
        return _pwd.verify(plain, phash)
    async def create_user(self, email, name, password, role="ROLE_USER"):
        hashed = _pwd.hash(password)
        user = UserORM(email=email, password=hashed, role=role)
        self.db.add(user); self.db.commit()
        return {"id": user.id, "email": user.email, "role": user.role}

# --- AuthCore Config ---
cfg = AuthCoreConfig(
    jwt=JwtConfig(
        enabled=True,
        secret="jwt-secret-long-enough",
        access_expires_seconds=1800,
        refresh_enabled=True,
        refresh_expires_seconds=2592000,
        prefix="/auth/jwt"
    ),
    session=SessionConfig(enabled=False, ttl_seconds=1800, prefix="/auth/session"),
    oauth=None,
    enabled=EndpointEnabled(login=True, refresh=True, logout=True, me=True)
)

# --- FastAPI App ---
app = FastAPI(title="AuthCore FastAPI Example")
app.add_middleware(SessionMiddleware, secret_key="session-secret")
auth = FastAPIAuthCore(app, cfg, UserRepositoryImpl())

@app.get("/protected")
async def protected_route(user=auth.verify()):
    return {"message": f"Hello, {user['email']}"}
```

✅ **Features**
- Full JWT authentication flow  
- Optional session & OAuth2 support  
- Built-in `/auth/*` endpoints  
- Role-based decorators via `require_permission`

---

## 🧰 Flask Integration

### Example: `app.py`

```python
from flask import Flask, jsonify
from authcore import (
    FlaskAuthCore, AuthCoreConfig, JwtConfig, SessionConfig,
    UserRepository
)
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Database Setup ---
engine = create_engine("sqlite:///./flask_test.db")
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
Base.metadata.create_all(bind=engine)

# --- Repository ---
class Repo(UserRepository):
    def __init__(self): self.db = SessionLocal()
    async def get_by_email(self, email): ...
    async def verify_password(self, plain, phash): ...
    async def create_user(self, email, name, password, role): ...

# --- Config ---
cfg = AuthCoreConfig(
    jwt=JwtConfig(enabled=True, secret="flask-demo-secret", access_expires_seconds=3600),
    session=None,
    oauth=None,
)

# --- App ---
app = Flask(__name__)
auth = FlaskAuthCore(app, cfg, Repo())

@app.route("/protected")
@auth.verify
def protected_route():
    user = auth.current_user()
    return jsonify({"email": user["email"]})
```

**Features**
- Middleware-free integration  
- Optional OAuth 2.0 login support  
- Compatible with Flask Blueprints  

---

## 🧱 Django Integration

### Example: `urls.py`

```python
from django.http import JsonResponse
from django.urls import path
from authcore import (
    AuthCoreConfig, JwtConfig, DjangoAuthCore, EndpointEnabled
)
from authcore.contracts import UserRepository
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from asgiref.sync import sync_to_async

User = get_user_model()

# --- Repository ---
class DjangoRepo(UserRepository):
    @sync_to_async
    def get_by_email(self, email):
        try:
            u = User.objects.get(email=email)
            return {"id": u.id, "email": u.email, "password": u.password, "roles": ["ROLE_USER"]}
        except User.DoesNotExist:
            return None
    @sync_to_async
    def verify_password(self, plain, phash):
        return check_password(plain, phash)

# --- Config ---
cfg = AuthCoreConfig(
    jwt=JwtConfig(enabled=True, secret="jwt-django-secret", access_expires_seconds=3600),
    session=None,
    oauth=None,
    enabled=EndpointEnabled(login=True, refresh=True, logout=True, me=True)
)

auth_core = DjangoAuthCore(cfg, DjangoRepo())

urlpatterns = [
    path("ping/", lambda r: JsonResponse({"ok": True})),
    *auth_core.get_urls()
]
```

✅ **Features**
- Integrates with Django ORM  
- Auto-registers `/auth/*` routes  
- Async-safe through `sync_to_async`  

---

## 🔐 Supported Authentication Modes

| Mode | Description |
|------|--------------|
| **JWT** | Stateless access tokens with optional refresh. |
| **Session** | Server-managed sessions using cookies. |
| **OAuth2** | Login with Google, GitHub, etc. |
| **2FA** | Adds OTP verification layer. |

---

## 🧩 RBAC (Role-Based Access Control)

You can protect endpoints using the `require_permission` decorator:

```python
from authcore import require_permission, RbacService

rbac = RbacService(
    roles={"ROLE_ADMIN": ["ADMIN_DASH", "USER_MANAGE"]},
    permissions={"ADMIN_DASH": "Dashboard Access", "USER_MANAGE": "Manage Users"}
)

@app.get("/admin")
@require_permission("ADMIN_DASH", rbac=rbac)
async def admin_page():
    return {"message": "Welcome, Admin!"}
```

---

## 🔐 2FA Example

```python
from authcore import TwoFAConfig

cfg = AuthCoreConfig(
    jwt=None,
    session=None,
    TwoFa=TwoFAConfig(
        enabled=True,
        otp_length=6,
        otp_type="numeric",
        otp_expires_in="5m",
        transport=lambda otp, user: print(f"Send {otp} to {user['email']}"),
        store_otp=lambda user_id, otp, exp: print("Storing OTP..."),
        get_stored_otp=lambda user_id: "123456",
        clear_otp=lambda user_id: print("Cleared OTP"),
    ),
)
```

✅ **Customizable** OTP transport (email, SMS, console, etc.)

---

## 📘 Summary

| Framework | Integration Class | Example Section |
|------------|------------------|----------------|
| **FastAPI** | `FastAPIAuthCore` | [FastAPI Integration](#-fastapi-integration) |
| **Flask**   | `FlaskAuthCore`   | [Flask Integration](#-flask-integration) |
| **Django**  | `DjangoAuthCore`  | [Django Integration](#-django-integration) |

All integrations use a **shared configuration system**, making it easy to migrate between frameworks or combine them in a microservice setup.

---

### 🧱 License
MIT License © 2025 AuthCore Contributors