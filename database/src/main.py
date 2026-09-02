"""FastAPI application entry point for Member 4 - Database Engine."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.api.router import api_router
from src.api.middleware import setup_middleware
from src.api.deps import check_rate_limit
from src.core.exceptions import DatabaseError

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
    
    # Check database connections
    from src.mongodb.connection import mongodb
    from src.neo4j.connection import neo4j
    
    mongodb_status = mongodb.health_check()
    neo4j_status = neo4j.health_check()
    
    logger.info(f"MongoDB: {mongodb_status['status']}")
    logger.info(f"Neo4j: {neo4j_status['status']}")
    
    # Run migrations
    try:
        from src.mongodb.migrations.migration_001 import Migration001
        migration = Migration001()
        result = migration.up()
        logger.info(f"Migration 001: {result}")
    except Exception as e:
        logger.warning(f"Migration failed: {e}")
    
    # Initialize integrations
    try:
        from src.integrations.member2_client import Member2Client
        from src.integrations.member3_client import Member3Client
        from src.integrations.member5_client import Member5Client
        
        # Test connections
        member2 = Member2Client()
        member3 = Member3Client()
        member5 = Member5Client()
        
        logger.info("Integration clients initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize integrations: {e}")
    
    yield
    
    # Shutdown
    from src.mongodb.connection import mongodb
    from src.neo4j.connection import neo4j
    mongodb.close()
    neo4j.close()
    logger.info("Shutting down Database Engine...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cyber Graph - Database & Graph Engine",
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
        "phase": "4 - Production Ready",
        "databases": {
            "mongodb": settings.mongodb_db,
            "neo4j": settings.neo4j_uri,
        },
        "rate_limit": {
            "remaining": rate_limit.get("remaining", 0),
        },
    }


@app.exception_handler(DatabaseError)
async def database_error_handler(request, exc: DatabaseError):
    """Handle custom database errors."""
    logger.error(f"Database error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": "DatabaseError",
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