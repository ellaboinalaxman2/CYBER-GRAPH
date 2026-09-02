# app/security/jwt.py
import jwt
from datetime import datetime, timedelta
from app.config.settings import settings
from fastapi import HTTPException, status

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Parse JWT_EXPIRES_IN (e.g., "1d", "1h")
        expires_in = settings.JWT_EXPIRES_IN
        if expires_in.endswith('d'):
            delta = timedelta(days=int(expires_in[:-1]))
        elif expires_in.endswith('h'):
            delta = timedelta(hours=int(expires_in[:-1]))
        else:
            delta = timedelta(minutes=int(expires_in))
        expire = datetime.utcnow() + delta
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")