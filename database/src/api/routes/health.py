"""Health check endpoints for Member 4 - Database Engine."""

from fastapi import APIRouter, status
from datetime import datetime

from src.core.logging import get_logger
from src.mongodb.connection import mongodb
from src.neo4j.connection import neo4j

router = APIRouter()
logger = get_logger("api.health")


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "database-engine",
    }


@router.get("/health/databases", status_code=status.HTTP_200_OK)
async def database_health():
    """Database health check endpoint."""
    mongodb_status = mongodb.health_check()
    neo4j_status = neo4j.health_check()
    
    all_healthy = mongodb_status["status"] == "healthy" and neo4j_status["status"] == "healthy"
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "mongodb": mongodb_status,
        "neo4j": neo4j_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }