from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class AuditAction(str, Enum):
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    EXPORT = "EXPORT"
    VERIFY = "VERIFY"
    ESCALATE = "ESCALATE"
    RESOLVE = "RESOLVE"
    ASSIGN = "ASSIGN"
    COMMENT = "COMMENT"
    BLOCKCHAIN_VERIFY = "BLOCKCHAIN_VERIFY"
    BLOCKCHAIN_STORE = "BLOCKCHAIN_STORE"

class AuditLogModel:
    """Audit log model for MongoDB"""
    
    def __init__(self, data: dict):
        self.data = data
    
    @staticmethod
    def schema() -> dict:
        """Audit log schema definition"""
        return {
            "audit_id": str,            # Unique audit identifier
            "user_id": str,             # User performing action
            "username": str,            # Username
            "action": AuditAction,      # Action performed
            "resource_type": str,       # Type of resource
            "resource_id": str,         # Resource identifier
            "details": str,             # Action details
            "ip_address": str,          # Client IP address
            "user_agent": str,          # User agent
            "before": Optional[Dict[str, Any]],  # Before state
            "after": Optional[Dict[str, Any]],   # After state
            "success": bool,            # Action success
            "error_message": Optional[str],  # Error message
            "duration_ms": Optional[float],  # Action duration
            "metadata": Dict[str, Any],  # Additional metadata
            "timestamp": datetime,      # Action timestamp
            "session_id": Optional[str],  # Session identifier
            "source_module": str       # Module performing action
        }
    
    @classmethod
    def create(cls, audit_data: dict) -> dict:
        """Create a new audit log document"""
        return {
            "audit_id": audit_data.get("audit_id"),
            "user_id": audit_data.get("user_id"),
            "username": audit_data.get("username"),
            "action": audit_data.get("action"),
            "resource_type": audit_data.get("resource_type"),
            "resource_id": audit_data.get("resource_id"),
            "details": audit_data.get("details"),
            "ip_address": audit_data.get("ip_address"),
            "user_agent": audit_data.get("user_agent"),
            "before": audit_data.get("before"),
            "after": audit_data.get("after"),
            "success": audit_data.get("success", True),
            "error_message": audit_data.get("error_message"),
            "duration_ms": audit_data.get("duration_ms"),
            "metadata": audit_data.get("metadata", {}),
            "timestamp": datetime.utcnow(),
            "session_id": audit_data.get("session_id"),
            "source_module": audit_data.get("source_module", "UNKNOWN")
        }