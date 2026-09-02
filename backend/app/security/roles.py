# app/security/roles.py
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

# Permission matrix (simplified)
ROLE_PERMISSIONS = {
    Role.ADMIN: ["read_all", "write_all", "delete_all", "manage_users"],
    Role.ANALYST: ["read_all", "write_alerts", "investigate"],
    Role.VIEWER: ["read_dashboard", "read_alerts"]
}

def has_permission(role: Role, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])