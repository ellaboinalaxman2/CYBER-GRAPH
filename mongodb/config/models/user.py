from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"

class UserModel:
    """User model for MongoDB"""
    
    def __init__(self, data: dict):
        self.data = data
    
    @staticmethod
    def schema() -> dict:
        """User schema definition"""
        return {
            "user_id": str,          # Unique identifier
            "username": str,          # Login username
            "email": str,             # User email
            "password_hash": str,     # Hashed password
            "role": UserRole,         # User role
            "full_name": str,         # Full name
            "department": Optional[str],  # Department
            "is_active": bool,        # Active status
            "created_at": datetime,   # Creation timestamp
            "updated_at": datetime,   # Last update timestamp
            "last_login": Optional[datetime],  # Last login time
            "permissions": List[str],  # Extended permissions
            "preferences": dict       # User preferences
        }
    
    @classmethod
    def create(cls, user_data: dict) -> dict:
        """Create a new user document"""
        return {
            "user_id": user_data.get("user_id"),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password_hash": user_data.get("password_hash"),
            "role": user_data.get("role", UserRole.VIEWER),
            "full_name": user_data.get("full_name"),
            "department": user_data.get("department"),
            "is_active": user_data.get("is_active", True),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": user_data.get("last_login"),
            "permissions": user_data.get("permissions", []),
            "preferences": user_data.get("preferences", {})
        }
    
    @classmethod
    def validate(cls, data: dict) -> tuple:
        """Validate user data"""
        required_fields = ["user_id", "username", "email", "password_hash", "full_name"]
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        if data.get("role") and data["role"] not in [r.value for r in UserRole]:
            return False, f"Invalid role: {data['role']}"
        
        return True, "Valid"