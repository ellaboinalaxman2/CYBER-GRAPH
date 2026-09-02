"""Health check endpoints."""

from fastapi import APIRouter, status
from datetime import datetime
from src.core.logging import get_logger

router = APIRouter()
logger = get_logger("api.health")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Service health status with timestamp
    """
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "ingestion-engine",
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness probe for orchestration (Kubernetes).
    
    Checks if the service is ready to accept traffic.
    """
    logger.debug("Readiness check requested")
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Liveness probe for orchestration (Kubernetes).
    
    Checks if the service is still running.
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }