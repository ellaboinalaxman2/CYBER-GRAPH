"""Authentication routes."""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

from src.auth import JWTHandler
from src.api.deps import get_current_user

router = APIRouter()
jwt_handler = JWTHandler()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    username: str
    role: str


class RefreshRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user and return tokens.
    
    Args:
        request: Login request
        
    Returns:
        LoginResponse: Authentication tokens
    """
    user = jwt_handler.authenticate(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    
    tokens = jwt_handler.create_tokens(user)
    
    return {
        **tokens,
        "username": user["username"],
        "role": user["role"],
    }


@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """
    Refresh an access token.
    
    Args:
        request: Refresh request
        
    Returns:
        dict: New tokens
    """
    tokens = jwt_handler.refresh_token(request.refresh_token)
    
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    return tokens


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout the current user.
    
    Args:
        current_user: Current user
        
    Returns:
        dict: Logout confirmation
    """
    # In a stateless JWT system, logout is handled client-side
    # This endpoint just confirms the logout
    return {
        "status": "logged_out",
        "username": current_user["username"],
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current user
        
    Returns:
        dict: User information
    """
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "authenticated": True,
    }