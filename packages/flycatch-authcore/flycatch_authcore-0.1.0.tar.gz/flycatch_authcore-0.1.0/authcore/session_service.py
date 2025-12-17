from __future__ import annotations
from typing import Dict, Optional, Any
from .config import SessionConfig
from .store_backends import InMemoryTTLStore, RedisTTLStore, SessionStore


class SessionService:
    def __init__(self, cfg: SessionConfig):
        self.cfg = cfg

        if cfg.store_backend == "redis":
            if not cfg.redis_url:
                raise ValueError("Session store_backend='redis' requires session.redis_url")
            kv = RedisTTLStore(cfg.redis_url, cfg.redis_prefix)
        else:
            kv = InMemoryTTLStore()

        self._store = SessionStore(kv, ttl_seconds=int(cfg.ttl_seconds))

    def create(self, user: Dict[str, Any]) -> str:
        return self._store.create(user)

    def get(self, sid: str) -> Optional[Dict[str, Any]]:
        return self._store.get(sid)

    def destroy(self, sid: str) -> None:
        self._store.destroy(sid)

    def refresh(self, sid: str) -> Optional[str]:
        return self._store.refresh(sid)
