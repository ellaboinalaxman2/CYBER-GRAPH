"""API router aggregator for Member 5 - Attack Engine."""

from fastapi import APIRouter, Depends
from src.api.routes import health, correlation, attacks, risk, mitre, alerts, docs
from src.api.deps import check_rate_limit

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(correlation.router, prefix="/correlation", tags=["correlation"])
api_router.include_router(attacks.router, prefix="/attacks", tags=["attacks"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(mitre.router, prefix="/mitre", tags=["mitre"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])


@api_router.get("/rate-limit-status")
async def get_rate_limit_status(rate_limit: dict = Depends(check_rate_limit)):
    """Get current rate limit status."""
    return {
        "status": "ok",
        "rate_limit": rate_limit,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z",
    }


__all__ = ["api_router"]