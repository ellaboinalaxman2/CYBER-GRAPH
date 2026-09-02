"""Permission management."""

from typing import Dict, List, Set, Optional
from enum import Enum


class Permission(str, Enum):
    """Permission types."""
    # Ingestion permissions
    INGEST_EVENT = "ingest:event"
    INGEST_BATCH = "ingest:batch"
    INGEST_STREAM = "ingest:stream"
    
    # Queue permissions
    QUEUE_PRODUCE = "queue:produce"
    QUEUE_CONSUME = "queue:consume"
    QUEUE_MANAGE = "queue:manage"
    
    # Worker permissions
    WORKER_START = "worker:start"
    WORKER_STOP = "worker:stop"
    WORKER_VIEW = "worker:view"
    
    # Admin permissions
    ADMIN_VIEW = "admin:view"
    ADMIN_MANAGE = "admin:manage"
    ADMIN_CONFIG = "admin:config"


class RolePermissions:
    """Role-based permission mappings."""
    
    PERMISSIONS = {
        "admin": {
            Permission.INGEST_EVENT,
            Permission.INGEST_BATCH,
            Permission.INGEST_STREAM,
            Permission.QUEUE_PRODUCE,
            Permission.QUEUE_CONSUME,
            Permission.QUEUE_MANAGE,
            Permission.WORKER_START,
            Permission.WORKER_STOP,
            Permission.WORKER_VIEW,
            Permission.ADMIN_VIEW,
            Permission.ADMIN_MANAGE,
            Permission.ADMIN_CONFIG,
        },
        "analyst": {
            Permission.INGEST_EVENT,
            Permission.INGEST_BATCH,
            Permission.INGEST_STREAM,
            Permission.QUEUE_PRODUCE,
            Permission.QUEUE_CONSUME,
            Permission.WORKER_VIEW,
            Permission.ADMIN_VIEW,
        },
        "viewer": {
            Permission.INGEST_EVENT,
            Permission.WORKER_VIEW,
            Permission.ADMIN_VIEW,
        },
    }
    
    @classmethod
    def has_permission(cls, role: str, permission: Permission) -> bool:
        """
        Check if a role has a permission.
        
        Args:
            role: Role name
            permission: Permission to check
            
        Returns:
            bool: True if has permission
        """
        return permission in cls.PERMISSIONS.get(role, set())
    
    @classmethod
    def get_permissions(cls, role: str) -> Set[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role: Role name
            
        Returns:
            Set[Permission]: Permissions
        """
        return cls.PERMISSIONS.get(role, set())