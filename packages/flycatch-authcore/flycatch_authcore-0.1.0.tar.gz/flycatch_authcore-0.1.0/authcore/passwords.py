from typing import Protocol
from passlib.context import CryptContext


class PasswordHasher(Protocol):
    def verify(self, plain_password: str, password_hash: str) -> bool: ...


class PasslibBcryptHasher:
    def __init__(self) -> None:
        self._ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return self._ctx.verify(plain_password, password_hash)
        except Exception:
            return False
