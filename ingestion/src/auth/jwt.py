"""JWT authentication handling."""

import jwt
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from src.core.logging import get_logger


class JWTHandler:
    """
    Handles JWT token creation and validation.
    
    Features:
    - Token creation
    - Token validation
    - Token refresh
    - Role-based access
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the JWT handler.
        
        Args:
            secret_key: Secret key for signing tokens
        """
        self.logger = get_logger("auth.jwt")
        self.secret_key = secret_key or self._get_secret_key()
        self.algorithm = "HS256"
        self.access_token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 86400 * 7  # 7 days
        
        # User database
        self.users = self._load_users()
    
    def _get_secret_key(self) -> str:
        """Get secret key from environment or generate one."""
        import os
        secret = os.environ.get("JWT_SECRET_KEY")
        if not secret:
            # Generate a secret key if not in environment
            import secrets
            secret = secrets.token_urlsafe(32)
            self.logger.warning("Using auto-generated JWT secret key")
        return secret
    
    def _load_users(self) -> Dict[str, Dict[str, Any]]:
        """Load users from database file."""
        users_file = Path("data/users.json")
        
        if users_file.exists():
            try:
                with open(users_file, 'r') as f:
                    users = json.load(f)
                    self.logger.info(f"Loaded {len(users)} users")
                    return users
            except Exception as e:
                self.logger.error(f"Failed to load users: {e}")
        
        # Create default users
        default_users = {
            "admin": {
                "username": "admin",
                "password": self._hash_password("admin123"),
                "role": "admin",
                "email": "admin@cybergraph.local",
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
            "analyst": {
                "username": "analyst",
                "password": self._hash_password("analyst123"),
                "role": "analyst",
                "email": "analyst@cybergraph.local",
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
            "viewer": {
                "username": "viewer",
                "password": self._hash_password("viewer123"),
                "role": "viewer",
                "email": "viewer@cybergraph.local",
                "created_at": datetime.utcnow().isoformat() + "Z",
            },
        }
        
        # Save default users
        users_file.parent.mkdir(parents=True, exist_ok=True)
        with open(users_file, 'w') as f:
            json.dump(default_users, f, indent=2)
        
        self.logger.info("Created default users")
        return default_users
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Optional[Dict[str, Any]]: User data if authenticated
        """
        user = self.users.get(username)
        
        if not user:
            return None
        
        if user.get("password") == self._hash_password(password):
            return {
                "username": username,
                "role": user.get("role", "viewer"),
                "email": user.get("email"),
            }
        
        return None
    
    def create_tokens(self, user: Dict[str, Any]) -> Dict[str, str]:
        """
        Create access and refresh tokens.
        
        Args:
            user: User data
            
        Returns:
            Dict[str, str]: Tokens
        """
        now = datetime.utcnow()
        
        # Access token
        access_payload = {
            "sub": user["username"],
            "role": user["role"],
            "iat": now,
            "exp": now + timedelta(seconds=self.access_token_expiry),
            "type": "access",
        }
        
        # Refresh token
        refresh_payload = {
            "sub": user["username"],
            "role": user["role"],
            "iat": now,
            "exp": now + timedelta(seconds=self.refresh_token_expiry),
            "type": "refresh",
        }
        
        access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expiry,
        }
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict[str, Any]]: Token payload if valid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if user exists
            if payload.get("sub") not in self.users:
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """
        Refresh an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            Optional[Dict[str, str]]: New tokens
        """
        payload = self.validate_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            return None
        
        user = {
            "username": payload["sub"],
            "role": payload["role"],
        }
        
        return self.create_tokens(user)
    
    def has_permission(self, token: str, required_role: str) -> bool:
        """
        Check if a token has the required role.
        
        Args:
            token: JWT token
            required_role: Required role
            
        Returns:
            bool: True if has permission
        """
        payload = self.validate_token(token)
        
        if not payload:
            return False
        
        user_role = payload.get("role", "viewer")
        
        # Role hierarchy: admin > analyst > viewer
        role_hierarchy = {
            "admin": 3,
            "analyst": 2,
            "viewer": 1,
        }
        
        return role_hierarchy.get(user_role, 0) >= role_hierarchy.get(required_role, 0)