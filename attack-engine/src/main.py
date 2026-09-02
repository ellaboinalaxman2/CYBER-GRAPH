"""FastAPI application entry point for Member 5 - Attack Engine."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.api.router import api_router
from src.api.middleware import setup_middleware
from src.api.deps import check_rate_limit
from src.core.exceptions import AttackEngineError

# Setup logging first
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        extra={
            "environment": settings.environment,
            "host": settings.api_host,
            "port": settings.api_port,
        }
    )
    
    # Initialize components
    logger.info("Attack Engine initialized")
    
    # Initialize integrations
    try:
        from src.integrations.member2_client import Member2Client
        from src.integrations.member3_client import Member3Client
        from src.integrations.member4_client import Member4Client
        from src.integrations.member6_client import Member6Client
        
        logger.info("Integration clients initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize integrations: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Attack Engine...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cyber Graph - Attack Engine",
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
async def root(rate_limit: dict = Depends(check_rate_limit)):
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None,
        "phase": "6 - Production Ready",
        "modules": ["correlation", "reconstruction", "attack_path", "risk", "mitre", "alert"],
        "rate_limit": {
            "remaining": rate_limit.get("remaining", 0),
        },
    }


@app.exception_handler(AttackEngineError)
async def attack_engine_error_handler(request, exc: AttackEngineError):
    """Handle custom Attack Engine errors."""
    logger.error(f"Attack Engine error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": "AttackEngineError",
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