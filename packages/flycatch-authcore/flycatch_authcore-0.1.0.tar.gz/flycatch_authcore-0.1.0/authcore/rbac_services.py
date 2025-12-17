# authcore/rbac_services.py
from typing import List, Dict


class RbacService:
    def __init__(self, roles: Dict[str, List[str]] = None, permissions: Dict[str, str] = None):
        self.permissions: Dict[str, str] = permissions or {}
        self.roles: Dict[str, List[str]] = roles or {}

    def set_roles(self, roles: Dict[str, List[str]]):
        self.roles = roles

    def set_permissions(self, permissions: Dict[str, str]):
        self.permissions = permissions

    def get_permissions_for_roles(self, roles: List[str]) -> List[str]:
        perms = set()
        for role in roles or []:
            key = f"ROLE_{role.upper()}" if not role.startswith("ROLE_") else role
            perms.update(self.roles.get(key, []))
        return list(perms)

    def has_permission(self, roles: List[str], permission: str) -> bool:
        return permission in self.get_permissions_for_roles(roles or [])
