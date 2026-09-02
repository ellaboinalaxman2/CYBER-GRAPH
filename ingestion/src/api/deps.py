"""API dependencies."""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth import JWTHandler, Permission, RolePermissions, _rate_limiter
from src.core.logging import get_logger

logger = get_logger("api.deps")

# JWT handler
jwt_handler = JWTHandler()


class Security:
    """Security dependency for API endpoints."""
    
    @staticmethod
    def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    ) -> Dict[str, Any]:
        """
        Get the current authenticated user.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Dict[str, Any]: User information
        """
        token = credentials.credentials
        payload = jwt_handler.validate_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {
            "username": payload.get("sub"),
            "role": payload.get("role", "viewer"),
            "token": token,
        }
    
    @staticmethod
    def require_permission(required_permission: Permission):
        """
        Require a specific permission.
        
        Args:
            required_permission: Permission required
            
        Returns:
            Callable: Dependency function
        """
        def dependency(current_user: Dict[str, Any] = Depends(Security.get_current_user)):
            role = current_user.get("role", "viewer")
            
            if not RolePermissions.has_permission(role, required_permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {required_permission}",
                )
            
            return current_user
        
        return dependency
    
    @staticmethod
    def rate_limit(key: str = "default_ip"):
        """
        Apply rate limiting.
        
        Args:
            key: Rate limit key
            
        Returns:
            Callable: Dependency function
        """
        def dependency(request: Request):
            # Determine the key based on type
            if key == "ip":
                limit_key = request.client.host if request.client else "unknown"
            elif key == "user":
                # Try to get user from token
                try:
                    credentials = HTTPBearer()(request)
                    token = credentials.credentials
                    payload = jwt_handler.validate_token(token)
                    limit_key = payload.get("sub", "unknown")
                except:
                    limit_key = "unauthenticated"
            else:
                limit_key = key
            
            allowed, info = _rate_limiter.check_limit(limit_key)
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info.get("limit", 0)),
                        "X-RateLimit-Reset": str(info.get("reset", 0)),
                    },
                )
            
            return {
                "key": limit_key,
                "rate_limit_info": info,
            }
        
        return dependency


# Convenience dependencies
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> Dict[str, Any]:
    """Get the current authenticated user."""
    return Security.get_current_user(credentials)


def require_admin():
    """Require admin role."""
    return Security.require_permission(Permission.ADMIN_MANAGE)


def require_analyst():
    """Require analyst role or higher."""
    return Security.require_permission(Permission.INGEST_EVENT)


def rate_limit_ip():
    """Apply IP-based rate limiting."""
    return Security.rate_limit("ip")


def rate_limit_user():
    """Apply user-based rate limiting."""
    return Security.rate_limit("user")