"""User models."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model."""
    
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="viewer", pattern="^(admin|analyst|viewer)$")
    email: Optional[str] = Field(None, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    active: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "secure_password",
                "role": "admin",
                "email": "admin@cybergraph.local",
            }
        }


class UserCreate(BaseModel):
    """User creation model."""
    
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: str = Field(default="viewer", pattern="^(admin|analyst|viewer)$")
    email: Optional[str] = None


class UserUpdate(BaseModel):
    """User update model."""
    
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = Field(None, pattern="^(admin|analyst|viewer)$")
    email: Optional[str] = None
    active: Optional[bool] = None