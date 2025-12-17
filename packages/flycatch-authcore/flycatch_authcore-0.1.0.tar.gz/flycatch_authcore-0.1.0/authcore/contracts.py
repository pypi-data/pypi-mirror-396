# authcore/contracts.py
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Protocol, Optional, Dict, Any, List
from .rbac_services import RbacService

@dataclass(frozen=True)
class Identity:
    id: str
    email: str
    name: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

    def attach_permissions(self, rbac: RbacService) -> "Identity":
        perms = rbac.get_permissions_for_roles(self.roles)
        return replace(self, permissions=perms)

class UserRepository(Protocol):
    """
    Client app must implement this (async).
    """

    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        ...

    async def verify_password(self, plain_password: str, password_hash: str) -> bool:
        ...

    async def create_user(self, email: str, name: str, password: Optional[str], role: str) -> Dict[str, Any]:
        ...

class IdentityService:
    def __init__(self, user_repo: UserRepository, rbac: RbacService):
        self.user_repo = user_repo
        self.rbac = rbac

    async def provision_user(
        self,
        email: str,
        name: str,
        default_role: str = "ROLE_USER",
        auto_provision: bool = True
    ) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email)
        if not user and auto_provision:
            user = await self.user_repo.create_user(email=email, name=name, password=None, role=default_role)
        if not user:
            raise ValueError("User not found and auto-provisioning disabled")

        roles: List[str] = user.get("roles") or [default_role]
        permissions: List[str] = self.rbac.get_permissions_for_roles(roles)
        user["roles"] = roles
        user["permissions"] = permissions
        return user
