# app/services/auth_service.py
from fastapi import HTTPException, status
from app.schemas.auth import UserRegister, UserLogin, UserOut
from app.security.password import hash_password, verify_password
from app.config.database import MongoDB
from typing import Optional
from datetime import datetime

class AuthService:
    @staticmethod
    async def register_user(user_data: UserRegister) -> UserOut:
        if not MongoDB.get_db():
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not connected")
        
        # Check if user already exists
        existing_user = await MongoDB.get_db().users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "role": user_data.role or "viewer",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await MongoDB.get_db().users.insert_one(user_dict)
        user_dict["id"] = str(result.inserted_id)
        
        return UserOut(**user_dict)

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[UserOut]:
        if not MongoDB.get_db():
            return None
        
        user = await MongoDB.get_db().users.find_one({"username": username})
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        user["id"] = str(user["_id"])
        return UserOut(**user)
