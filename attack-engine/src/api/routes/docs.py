"""API documentation routes for Member 5 - Attack Engine."""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Any

from src.core.config import settings

router = APIRouter()


@router.get("/docs/info")
async def get_api_info() -> Dict[str, Any]:
    """Get API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Cyber Graph - Attack Engine",
        "phase": "6 - Production Ready",
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": [
            "correlation",
            "reconstruction",
            "attack_path",
            "risk",
            "mitre",
            "alert",
        ],
        "endpoints": {
            "health": "/api/v1/health",
            "correlation": "/api/v1/correlation",
            "attacks": "/api/v1/attacks",
            "risk": "/api/v1/risk",
            "mitre": "/api/v1/mitre",
            "alerts": "/api/v1/alerts",
        },
    }


@router.get("/docs/health")
async def get_api_health() -> Dict[str, Any]:
    """Get API health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": settings.app_version,
    }