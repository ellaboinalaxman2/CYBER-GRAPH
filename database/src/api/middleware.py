"""API middleware for Member 4 - Database Engine."""

from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time

from src.core.config import settings  # Add this import
from src.core.logging import get_logger

logger = get_logger("api.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and log it."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration, 2),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and add security headers."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Response-Time"] = str(round(time.time() - request.state.start_time if hasattr(request.state, 'start_time') else 0, 2))
        
        return response


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking response time."""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and track response time."""
        request.state.start_time = time.time()
        response = await call_next(request)
        return response


def setup_middleware(app):
    """
    Setup all middleware for the application.
    
    Args:
        app: FastAPI application
    """
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