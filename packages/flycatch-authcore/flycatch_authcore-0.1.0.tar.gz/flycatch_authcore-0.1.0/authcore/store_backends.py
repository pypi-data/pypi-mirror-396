from __future__ import annotations
from typing import Optional, Dict, Any, Protocol, Tuple
import json
import time
import secrets
import threading


class KeyValueTTLStore(Protocol):
    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None: ...
    def get_json(self, key: str) -> Optional[Dict[str, Any]]: ...
    def delete(self, key: str) -> None: ...
    def exists(self, key: str) -> bool: ...


class InMemoryTTLStore(KeyValueTTLStore):
    """
    Thread-safe in-memory TTL store.
    NOTE: not safe for multi-process/multi-pod. Use Redis store in production.
    """
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._data: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def _now(self) -> float:
        return time.time()

    def _cleanup_one(self, key: str) -> None:
        exp, _ = self._data.get(key, (0.0, {}))
        if exp and exp < self._now():
            self._data.pop(key, None)

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        with self._lock:
            exp = self._now() + max(1, int(ttl_seconds))
            self._data[key] = (exp, value)

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            self._cleanup_one(key)
            item = self._data.get(key)
            if not item:
                return None
            exp, value = item
            if exp < self._now():
                self._data.pop(key, None)
                return None
            return value

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def exists(self, key: str) -> bool:
        return self.get_json(key) is not None


class RedisTTLStore(KeyValueTTLStore):
    """
    Redis-backed TTL store.
    Requires: pip install redis
    """
    def __init__(self, redis_url: str, prefix: str) -> None:
        try:
            import redis  # type: ignore
        except Exception as e:
            raise ImportError("Redis store selected but 'redis' package not installed. pip install redis") from e

        self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self._prefix = prefix

    def _k(self, key: str) -> str:
        return f"{self._prefix}{key}"

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
        payload = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
        self._redis.set(self._k(key), payload, ex=max(1, int(ttl_seconds)))

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self._redis.get(self._k(key))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    def delete(self, key: str) -> None:
        self._redis.delete(self._k(key))

    def exists(self, key: str) -> bool:
        return bool(self._redis.exists(self._k(key)))


# ---- Session Store ----
class SessionStore:
    def __init__(self, kv: KeyValueTTLStore, ttl_seconds: int) -> None:
        self.kv = kv
        self.ttl = ttl_seconds

    def create(self, user: Dict[str, Any]) -> str:
        sid = secrets.token_urlsafe(32)
        self.kv.set_json(sid, {"user": user}, self.ttl)
        return sid

    def get(self, sid: str) -> Optional[Dict[str, Any]]:
        data = self.kv.get_json(sid)
        if not data:
            return None
        return data.get("user")

    def destroy(self, sid: str) -> None:
        self.kv.delete(sid)

    def refresh(self, sid: str) -> Optional[str]:
        user = self.get(sid)
        if not user:
            return None
        self.destroy(sid)
        return self.create(user)


# ---- OAuth Temp Code Store ----
class OAuthTempCodeStore:
    def __init__(self, kv: KeyValueTTLStore, ttl_seconds: int) -> None:
        self.kv = kv
        self.ttl = ttl_seconds

    def mint(self, provider: str, user: Dict[str, Any]) -> str:
        code = secrets.token_hex(32)
        self.kv.set_json(code, {"provider": provider, "user": user}, self.ttl)
        return code

    def pop(self, provider: str, code: str) -> Optional[Dict[str, Any]]:
        data = self.kv.get_json(code)
        if not data:
            return None
        if data.get("provider") != provider:
            return None
        self.kv.delete(code)
        user = data.get("user")
        return user if isinstance(user, dict) else None


# ---- Refresh Token Rotation Store ----
class RefreshRotationStore:
    """
    Stores single-use refresh token JTIs.
    - issue(): marks JTI as valid
    - consume(): atomically invalidates JTI
    """
    def __init__(self, kv: KeyValueTTLStore, ttl_seconds: int) -> None:
        self.kv = kv
        self.ttl = ttl_seconds
        self._lock = threading.RLock()

    def issue(self, jti: str) -> None:
        self.kv.set_json(jti, {"ok": True}, self.ttl)

    def consume(self, jti: str) -> bool:
        # In-memory version is protected by lock; Redis version is best-effort via GET+DEL.
        with self._lock:
            if not self.kv.exists(jti):
                return False
            self.kv.delete(jti)
            return True
