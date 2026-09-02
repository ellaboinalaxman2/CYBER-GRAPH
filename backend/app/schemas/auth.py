# app/schemas/auth.py
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "viewer"

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str