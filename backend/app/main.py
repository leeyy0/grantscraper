"""FastAPI application for grant filtering pipeline."""

from fastapi import FastAPI

from app.routers import grant_filtering

# Initialize FastAPI app
app = FastAPI(title="Grant Scraper API", version="1.0.0")

# Include routers
app.include_router(grant_filtering.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
