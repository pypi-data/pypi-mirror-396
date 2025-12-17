from __future__ import annotations
import jwt
from typing import Dict, Any, Optional
from datetime import datetime
import secrets

from .config import JwtConfig
from .utils import utcnow, exp_in, public_identity
from .store_backends import InMemoryTTLStore, RedisTTLStore, RefreshRotationStore


class JWTService:
    def __init__(self, cfg: JwtConfig):
        self.cfg = cfg

        self._refresh_rotation_store: Optional[RefreshRotationStore] = None
        if cfg.refresh_rotation_enabled:
            if cfg.refresh_store_backend == "redis":
                if not cfg.refresh_store_redis_url:
                    raise ValueError("jwt.refresh_store_backend='redis' requires jwt.refresh_store_redis_url")
                kv = RedisTTLStore(cfg.refresh_store_redis_url, cfg.refresh_store_redis_prefix)
            else:
                kv = InMemoryTTLStore()
            self._refresh_rotation_store = RefreshRotationStore(kv, ttl_seconds=int(cfg.refresh_expires_seconds))

    def _encode(self, claims: Dict[str, Any], expires_at: datetime) -> str:
        payload = {**claims, "exp": int(expires_at.timestamp()), "iat": int(utcnow().timestamp())}
        headers = {"alg": self.cfg.algorithm, "typ": "JWT"}
        return jwt.encode(payload, self.cfg.secret, algorithm=self.cfg.algorithm, headers=headers)

    def decode(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, self.cfg.secret, algorithms=[self.cfg.algorithm])

    def issue_access(self, user: dict) -> str:
        ident = public_identity(user)
        claims = {
            "sub": ident["id"],
            "email": ident["email"],
            "name": ident["name"],
            "roles": ident["roles"],
            "permissions": ident["permissions"],
            "type": "access",
        }
        return self._encode(claims, exp_in(self.cfg.access_expires_seconds))

    def issue_refresh(self, user: dict) -> Optional[str]:
        if not self.cfg.refresh_enabled:
            return None
        ident = public_identity(user)

        jti = secrets.token_hex(16) if self.cfg.refresh_rotation_enabled else None
        claims: Dict[str, Any] = {"sub": ident["id"], "email": ident["email"], "type": "refresh"}
        if jti:
            claims["jti"] = jti

        token = self._encode(claims, exp_in(self.cfg.refresh_expires_seconds))

        if self._refresh_rotation_store and jti:
            self._refresh_rotation_store.issue(jti)

        return token

    def verify_access(self, token: str) -> Dict[str, Any]:
        data = self.decode(token)
        if data.get("type") != "access":
            raise jwt.InvalidTokenError("Not an access token")
        return data

    def verify_refresh(self, token: str) -> Dict[str, Any]:
        data = self.decode(token)
        if data.get("type") != "refresh":
            raise jwt.InvalidTokenError("Not a refresh token")

        # Refresh rotation: token must be single-use
        if self._refresh_rotation_store:
            jti = data.get("jti")
            if not jti or not isinstance(jti, str):
                raise jwt.InvalidTokenError("Refresh token missing jti")
            if not self._refresh_rotation_store.consume(jti):
                raise jwt.InvalidTokenError("Refresh token already used or revoked")

        return data
