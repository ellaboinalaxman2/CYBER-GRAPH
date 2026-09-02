# app/middleware/auth_middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Authentication temporarily disabled for app development.
        # Provide a default anonymous identity so routes depending on request.state.user
        # continue to function without login or JWT enforcement.
        request.state.user = getattr(request.state, "user", {"userId": "anonymous", "username": "anonymous"})
        return await call_next(request)
