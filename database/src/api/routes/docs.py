"""API documentation routes for Member 4 - Database Engine."""

from fastapi import APIRouter, status
from datetime import datetime
from typing import Dict, Any

from src.core.config import settings

router = APIRouter()


@router.get("/docs/info")
async def get_api_info() -> Dict[str, Any]:
    """
    Get API information.
    
    Returns:
        Dict[str, Any]: API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Cyber Graph - Database & Graph Engine",
        "phase": "4 - Production Ready",
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "databases": {
            "mongodb": {
                "name": settings.mongodb_db,
                "collections": ["events", "alerts", "incidents"],
                "status": "connected",
            },
            "neo4j": {
                "uri": settings.neo4j_uri,
                "status": "connected",
            },
        },
        "endpoints": {
            "health": "/api/v1/health",
            "events": "/api/v1/events",
            "alerts": "/api/v1/alerts",
            "incidents": "/api/v1/incidents",
            "graph": "/api/v1/graph",
        },
    }


@router.get("/docs/health")
async def get_api_health() -> Dict[str, Any]:
    """
    Get API health status.
    
    Returns:
        Dict[str, Any]: Health status
    """
    from src.mongodb.connection import mongodb
    from src.neo4j.connection import neo4j
    
    mongodb_status = mongodb.health_check()
    neo4j_status = neo4j.health_check()
    
    return {
        "status": "healthy" if mongodb_status["status"] == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "components": {
            "mongodb": mongodb_status,
            "neo4j": neo4j_status,
        },
    }


@router.get("/docs/version")
async def get_version() -> Dict[str, Any]:
    """
    Get API version.
    
    Returns:
        Dict[str, Any]: Version information
    """
    return {
        "version": settings.app_version,
        "build": datetime.utcnow().isoformat() + "Z",
        "environment": settings.environment,
    }