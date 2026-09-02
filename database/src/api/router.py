"""API router aggregator for Member 4 - Database Engine."""

from fastapi import APIRouter, Depends
from src.api.routes import health, events, graph, alerts, incidents, docs
from src.api.deps import check_rate_limit

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(graph.router, prefix="/graph", tags=["graph"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])


@api_router.get("/rate-limit-status")
async def get_rate_limit_status(rate_limit: dict = Depends(check_rate_limit)):
    """
    Get current rate limit status.
    
    Returns:
        dict: Rate limit status
    """
    return {
        "status": "ok",
        "rate_limit": rate_limit,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["api_router"]