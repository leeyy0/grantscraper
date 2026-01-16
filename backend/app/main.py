"""FastAPI application for grant filtering pipeline."""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.core.config import setup_logging
from app.routers import grants_router, pipeline_router, results_router

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    logger.info("Grant Scraper API starting up...")
    yield
    # Shutdown
    logger.info("Grant Scraper API shutting down...")


# Initialize FastAPI app with lifespan
app = FastAPI(title="Grant Scraper API", version="1.0.0", lifespan=lifespan)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses."""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Log response
    duration = time.time() - start_time
    logger.info(
        f"Response: {request.method} {request.url.path} - "
        f"Status: {response.status_code} - Duration: {duration:.3f}s"
    )

    return response


# Include routers
app.include_router(pipeline_router)
app.include_router(grants_router)
app.include_router(results_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
