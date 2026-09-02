"""API middleware for Member 5 - Attack Engine."""

from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger("api.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and log it."""
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = (time.time() - start_time) * 1000
        
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration, 2),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and add security headers."""
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking response time."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and track response time."""
        request.state.start_time = time.time()
        response = await call_next(request)
        return response


def setup_middleware(app):
    """Setup all middleware for the application."""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getattr(settings, 'CORS_ORIGINS', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted Hosts
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"],
    )
    
    # Response Time
    app.add_middleware(ResponseTimeMiddleware)
    
    # Request Logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)