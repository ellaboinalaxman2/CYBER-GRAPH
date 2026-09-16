from typing import Optional, List, Dict, Any
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from ..models.user import UserModel, UserRole
from .base_repository import BaseRepository

class UserRepository(BaseRepository):
    """Repository for user operations"""
    
    def __init__(self):
        super().__init__("users")
    
    def create_user(self, user_data: Dict[str, Any]) -> InsertOneResult:
        """Create a new user"""
        user_doc = UserModel.create(user_data)
        return self.create(user_doc)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        return self.find_by_id(user_id, "user_id")
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        return self.find_one({"username": username})
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        return self.find_one({"email": email})
    
    def get_users(self, limit: int = 100, skip: int = 0, 
                  active_only: bool = True) -> List[Dict[str, Any]]:
        """Get list of users"""
        query = {"is_active": True} if active_only else {}
        return self.find(query, limit=limit, skip=skip, sort=[("created_at", -1)])
    
    def get_users_by_role(self, role: UserRole) -> List[Dict[str, Any]]:
        """Get users by role"""
        return self.find({"role": role, "is_active": True})
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> UpdateResult:
        """Update user"""
        # Remove fields that shouldn't be updated directly
        forbidden_fields = ["user_id", "password_hash", "created_at"]
        for field in forbidden_fields:
            update_data.pop(field, None)
        return self.update_by_id(user_id, update_data, "user_id")
    
    def update_password(self, user_id: str, password_hash: str) -> UpdateResult:
        """Update user password"""
        return self.update_by_id(user_id, {"password_hash": password_hash}, "user_id")
    
    def update_last_login(self, user_id: str) -> UpdateResult:
        """Update last login time"""
        from datetime import datetime
        return self.update_by_id(user_id, {"last_login": datetime.utcnow()}, "user_id")
    
    def delete_user(self, user_id: str) -> DeleteResult:
        """Delete user"""
        return self.delete_by_id(user_id, "user_id")
    
    def deactivate_user(self, user_id: str) -> UpdateResult:
        """Deactivate user"""
        return self.update_by_id(user_id, {"is_active": False}, "user_id")
    
    def activate_user(self, user_id: str) -> UpdateResult:
        """Activate user"""
        return self.update_by_id(user_id, {"is_active": True}, "user_id")
    
    def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by username, email, or full_name"""
        return self.find({
            "$or": [
                {"username": {"$regex": search_term, "$options": "i"}},
                {"email": {"$regex": search_term, "$options": "i"}},
                {"full_name": {"$regex": search_term, "$options": "i"}}
            ]
        })
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics"""
        total = self.count()
        active = self.count({"is_active": True})
        by_role = self.aggregate([
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ])
        return {
            "total_users": total,
            "active_users": active,
            "inactive_users": total - active,
            "users_by_role": by_role
        }