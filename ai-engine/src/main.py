"""FastAPI application entry point for Member 3 - AI Engine."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.api.router import api_router
from src.api.middleware import setup_middleware
from src.core.exceptions import AIEngineError
from src.model_registry import ModelRegistry

# Setup logging first
setup_logging()
logger = get_logger("main")

# Global registry
_model_registry = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events.
    """
    global _model_registry
    
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        extra={
            "environment": settings.environment,
            "host": settings.api_host,
            "port": settings.api_port,
        }
    )
    
    # Initialize model registry
    _model_registry = ModelRegistry()
    logger.info("Model registry initialized")
    
    # Log model status
    active_model = _model_registry.get_model()
    if active_model:
        logger.info(f"Active model: {active_model.name} v{active_model.version}")
    else:
        logger.warning("No active model found")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Engine...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cyber Graph - AI Engine (GraphSAGE for Anomaly Detection)",
    lifespan=lifespan,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Setup middleware
setup_middleware(app)

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint with service information."""
    active_model = _model_registry.get_model() if _model_registry else None
    
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None,
        "model": {
            "name": active_model.name if active_model else "None",
            "version": active_model.version if active_model else "None",
            "status": active_model.status if active_model else "not_loaded",
        },
    }


@app.exception_handler(AIEngineError)
async def ai_engine_error_handler(request, exc: AIEngineError):
    """Handle custom AI Engine errors."""
    logger.error(f"AI Engine error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": "AIEngineError",
            "message": exc.message,
            "details": exc.details,
        }
    )


@app.exception_handler(Exception)
async def general_error_handler(request, exc: Exception):
    """Handle unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
        }
    )