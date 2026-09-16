from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from ..models.user import UserRole

class UserSchema(BaseModel):
    """User schema for validation"""
    
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    password_hash: str = Field(..., description="Hashed password")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    department: Optional[str] = Field(None, max_length=50, description="Department")
    is_active: bool = Field(default=True, description="Active status")
    permissions: List[str] = Field(default=[], description="Extended permissions")
    preferences: dict = Field(default={}, description="User preferences")
    last_login: Optional[datetime] = Field(None, description="Last login time")
    
    class Config:
        use_enum_values = True
        
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain alphanumeric, underscore and hyphen')
        return v

class UserCreateSchema(BaseModel):
    """Schema for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: UserRole = UserRole.VIEWER
    department: Optional[str] = None

class UserUpdateSchema(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    department: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    preferences: Optional[dict] = None