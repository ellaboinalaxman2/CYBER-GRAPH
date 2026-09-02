"""API router aggregator for Member 3 - AI Engine."""

from fastapi import APIRouter
from src.api.routes import health, prediction, explain

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(prediction.router, prefix="/predict", tags=["prediction"])
api_router.include_router(explain.router, prefix="/explain", tags=["explainability"])

# Also add direct routes for model status
@api_router.get("/model/status")
async def model_status():
    """Get model status."""
    from src.api.routes.prediction import get_model_status
    return await get_model_status()

@api_router.get("/model/info")
async def model_info():
    """Get model information."""
    from src.api.routes.prediction import get_model_info
    return await get_model_info()

__all__ = ["api_router"]