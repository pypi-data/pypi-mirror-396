# authcore/__init__.py
from .config import (
    AuthCoreConfig, JwtConfig, SessionConfig, EndpointsConfig,
    EndpointEnabled, OAuth2Config, OAuth2ProviderConfig, TokenResponse,
    TwoFAConfig
)
from .contracts import Identity, UserRepository, IdentityService
from .passwords import PasswordHasher, PasslibBcryptHasher
from .jwt_service import JWTService
from .session_service import SessionService
from .rbac_services import RbacService
from .permission_decorator import require_permission

try:
    from .adapters.fastapi_adapter import FastAPIAuthCore
except Exception:
    class FastAPIAuthCore:
        def __init__(self, *_, **__):
            raise ImportError("FastAPI adapter requires fastapi/starlette installed. pip install fastapi")

try:
    from .adapters.flask_adapter import FlaskAuthCore
except Exception:
    class FlaskAuthCore:
        def __init__(self, *_, **__):
            raise ImportError("Flask adapter requires flask installed. pip install flask")

try:
    from .adapters.django_adapter import DjangoAuthCore
except Exception:
    class DjangoAuthCore:
        def __init__(self, *_, **__):
            raise ImportError("Django adapter requires django installed. pip install django")

__all__ = [
    "AuthCoreConfig", "JwtConfig", "SessionConfig", "EndpointsConfig",
    "EndpointEnabled", "OAuth2Config", "OAuth2ProviderConfig", "TokenResponse",
    "Identity", "UserRepository", "IdentityService",
    "JWTService", "SessionService",
    "PasswordHasher", "PasslibBcryptHasher",
    "FastAPIAuthCore", "FlaskAuthCore", "DjangoAuthCore",
    "RbacService", "require_permission",
    "TwoFAConfig"
]
