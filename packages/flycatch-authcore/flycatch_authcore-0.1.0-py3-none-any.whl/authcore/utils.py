# authcore/utils.py
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

def exp_in(seconds: int) -> datetime:
    return utcnow() + timedelta(seconds=seconds)

def public_identity(user: dict) -> Dict[str, Any]:
    return {
        "id": str(user.get("id")),
        "email": user.get("email"),
        "name": user.get("name"),
        "roles": list(user.get("roles", [])),
        "permissions": list(user.get("permissions", [])),
    }
