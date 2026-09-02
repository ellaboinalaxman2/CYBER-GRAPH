"""Health check endpoints for Member 3 - AI Engine."""

from fastapi import APIRouter, status
from datetime import datetime
import torch

from src.core.logging import get_logger
from src.core.config import settings

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
        "service": "ai-engine",
        "version": settings.app_version,
    }


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """
    Readiness probe for orchestration (Kubernetes).
    
    Checks if the service is ready to accept traffic.
    """
    # Check if model is loaded (will be implemented in later phases)
    model_ready = True
    
    return {
        "ready": model_ready,
        "model_loaded": model_ready,
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


@router.get("/health/gpu", status_code=status.HTTP_200_OK)
async def gpu_status():
    """
    GPU status endpoint.
    
    Returns:
        dict: GPU availability and information
    """
    gpu_info = {
        "available": torch.cuda.is_available(),
        "count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "device": settings.gpu_device if settings.use_gpu else None,
    }
    
    if torch.cuda.is_available():
        gpu_info["name"] = torch.cuda.get_device_name(settings.gpu_device)
        gpu_info["memory_total"] = torch.cuda.get_device_properties(
            settings.gpu_device
        ).total_memory / 1e9  # GB
    
    return {
        "status": "ok",
        "gpu": gpu_info,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }