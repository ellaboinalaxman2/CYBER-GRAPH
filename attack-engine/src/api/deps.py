"""API dependencies for Member 5 - Attack Engine."""

from typing import Dict, Any
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
import time
from collections import defaultdict

from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger("api.deps")


class RateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.logger = get_logger("api.rate_limiter")
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed."""
        limit = getattr(settings, 'API_RATE_LIMIT', 100)
        window = getattr(settings, 'API_RATE_LIMIT_WINDOW', 60)
        
        now = time.time()
        cutoff = now - window
        
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > cutoff]
        
        if len(self.requests[client_ip]) >= limit:
            return False
        
        self.requests[client_ip].append(now)
        return True


_rate_limiter = RateLimiter()


async def get_client_ip(request: Request) -> str:
    """Get client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


async def check_rate_limit(request: Request) -> Dict[str, Any]:
    """Check rate limit for request."""
    client_ip = await get_client_ip(request)
    
    if not _rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(getattr(settings, 'API_RATE_LIMIT', 100)),
                "X-RateLimit-Reset": str(int(time.time()) + getattr(settings, 'API_RATE_LIMIT_WINDOW', 60)),
            }
        )
    
    return {"client_ip": client_ip}