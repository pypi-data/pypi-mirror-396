# authcore/permission_decorator.py
from functools import wraps
from typing import Callable, Dict, Any
from .rbac_services import RbacService

class PermissionDenied(Exception):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)
        self.message = message

def require_permission(permission: str, rbac: RbacService):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user: Dict[str, Any] = kwargs.get("user")
            if user is None:
                raise PermissionDenied("User object missing")
            roles = user.get("roles") or []
            if not rbac.has_permission(roles, permission):
                raise PermissionDenied("Permission denied")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
