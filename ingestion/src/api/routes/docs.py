"""API documentation routes."""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/docs/info")
async def get_api_info():
    """
    Get API information.
    
    Returns:
        dict: API information
    """
    return {
        "name": "Cyber Graph - Ingestion API",
        "version": "1.0.0",
        "description": "Security event ingestion engine API",
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "endpoints": {
            "auth": {
                "login": "/api/v1/auth/login",
                "refresh": "/api/v1/auth/refresh",
                "logout": "/api/v1/auth/logout",
                "me": "/api/v1/auth/me",
            },
            "ingestion": {
                "sources": "/api/v1/ingestion/sources",
                "collect": "/api/v1/ingestion/collect/{source_type}",
                "pipeline": "/api/v1/ingestion/pipeline/process",
                "batch": "/api/v1/ingestion/ingest/batch",
                "stream": "/api/v1/ingestion/ingest/stream",
            },
            "queue": {
                "create": "/api/v1/queue/create",
                "produce": "/api/v1/queue/produce",
                "consume": "/api/v1/queue/consume",
                "stats": "/api/v1/queue/stats",
            },
            "workers": {
                "start": "/api/v1/workers/start",
                "stop": "/api/v1/workers/stop",
                "stats": "/api/v1/workers/stats",
            },
        },
        "authentication": {
            "type": "Bearer Token (JWT)",
            "roles": ["admin", "analyst", "viewer"],
        },
        "rate_limits": {
            "default": "100 requests per minute (IP)",
            "authenticated": "200 requests per minute (User)",
        },
    }


@router.get("/docs/health")
async def get_api_health():
    """
    Get API health status.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }