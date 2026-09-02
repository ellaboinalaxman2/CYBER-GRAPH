"""API router aggregator."""

from fastapi import APIRouter
from src.api.routes import health, ingestion, auth, docs

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(docs.router, prefix="/docs", tags=["docs"])