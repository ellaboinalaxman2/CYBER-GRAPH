# app/models/user.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    hashed_password: str
    role: str = "viewer"  # admin, analyst, viewer
    created_at: Optional[str] = None
    disabled: bool = False

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "username": "analyst1",
                "email": "analyst1@cybergraph.local",
                "role": "analyst"
            }
        }