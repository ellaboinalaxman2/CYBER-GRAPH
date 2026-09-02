"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.logging import setup_logging, get_logger
from src.api.router import api_router
from src.api.middleware import setup_middleware
from src.core.exceptions import IngestionError
from src.queue import QueueManager
from src.workers import EventWorker, WorkerPool
from src.pipeline import Pipeline

# Setup logging first
setup_logging()
logger = get_logger("main")

# Global instances
_queue_manager = QueueManager()
_worker_pool = WorkerPool(max_workers=4)
_event_worker = EventWorker()
_pipeline = Pipeline()


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
    
    # Initialize queue
    try:
        _queue_manager.start()
        _queue_manager.create_queue("events", max_retries=3)
        _worker_pool.add_worker(_event_worker)
        _worker_pool.start()
        logger.info("Queue manager and workers started")
    except Exception as e:
        logger.warning(f"Queue initialization failed (Redis may not be running): {e}")
        logger.info("Running in standalone mode without queue")
    
    yield
    
    # Shutdown
    try:
        _worker_pool.stop()
        _queue_manager.stop()
        logger.info("Queue manager and workers stopped")
    except Exception as e:
        logger.warning(f"Queue shutdown error: {e}")
    
    logger.info("Shutting down ingestion service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cyber Graph - Security Event Ingestion Engine",
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
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else None,
    }


@app.exception_handler(IngestionError)
async def ingestion_error_handler(request, exc: IngestionError):
    """Handle custom ingestion errors."""
    logger.error(f"Ingestion error: {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=400,
        content={
            "error": "IngestionError",
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