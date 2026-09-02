"""Health check endpoints for Member 5 - Attack Engine."""

from fastapi import APIRouter, status
from datetime import datetime

from src.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.health")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "attack-engine",
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness check endpoint."""
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }