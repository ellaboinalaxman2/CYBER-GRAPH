# app/api/routes/auth.py
from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel
from app.api.controllers.auth_controller import AuthController
from app.security.jwt import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

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
    token_type: str

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str

@router.post("/register")
async def register(user_data: UserRegister):
    user = await AuthController.register_user(user_data)
    access_token = create_access_token(data={"sub": user.id, "userId": user.id, "role": user.role})
    return {"success": True, "token": access_token, "access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/login")
async def login(login_data: UserLogin):
    user = await AuthController.authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.id, "userId": user.id, "role": user.role})
    return {"success": True, "token": access_token, "access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me")
async def get_me(request: Request):
    user = await AuthController.get_current_user_from_id(request.state.user.get("userId"))
    return {"success": True, "user": user}

@router.post("/logout")
async def logout():
    return {"success": True, "message": "Logged out successfully"}
