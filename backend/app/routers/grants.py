"""Grant management endpoints for scraping and refreshing grant data."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.services.refresh_status import (
    RefreshPhase,
    create_job_id,
    get_refresh_status,
)
from app.services.scraper import scrape_and_refresh_grants

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/grants", tags=["grants"])


@router.post("/refresh")
async def refresh_grants(
    headless: bool = True,
    take_screenshots: bool = False,
):
    """
    Start a grant refresh job to scrape the latest open grants.

    This endpoint returns immediately with a job_id. Use the /refresh-status
    endpoint to check the progress of the scraping operation.

    The scraper:
    1. Scrapes the grants listing page for open grants
    2. Filters out closed grants automatically
    3. Extracts detailed information from each grant page
    4. Updates the database (creates new grants or updates existing ones by URL)

    The scraper automatically filters out closed grants by checking for:
    - "Closed" status indicators
    - "Applications closed" text

    Args:
        headless: Run browser in headless mode (default: True)
        take_screenshots: Save debug screenshots during scraping (default: False)

    Returns:
        Job information including:
        - job_id: Unique identifier to track this refresh operation
        - message: Confirmation message
        - status_endpoint: URL to check job status
    """
    # Create unique job ID
    job_id = create_job_id()

    logger.info(
        f"Starting grant refresh job {job_id} (headless={headless}, "
        f"screenshots={take_screenshots})"
    )

    # Start scraping in background - fire and forget
    asyncio.create_task(
        asyncio.to_thread(
            scrape_and_refresh_grants,
            take_screenshots=take_screenshots,
            headless=headless,
            save_to_db=True,
            job_id=job_id,
        )
    )

    logger.info(f"Grant refresh job {job_id} started in background")

    return {
        "job_id": job_id,
        "message": "Grant refresh job started",
        "status_endpoint": f"/grants/refresh-status/{job_id}",
    }


@router.get("/refresh-status/{job_id}")
async def get_refresh_status_endpoint(job_id: str):
    """
    Get the status of a grant refresh job.

    Args:
        job_id: The job ID returned from the /refresh endpoint

    Returns:
        Current status of the refresh job including:
        - job_id: The job identifier
        - phase: Current phase (starting, navigating, extracting_links, etc.)
        - total_found: Number of grants found (when available)
        - current_grant: Current grant being processed (when available)
        - grants_saved: Number of grants saved to database (when available)
        - message: Human-readable status message
        - error: Error message if operation failed
    """
    logger.debug(f"Status check for refresh job {job_id}")

    status = get_refresh_status(job_id)

    if not status:
        logger.warning(f"No status found for job {job_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Refresh job {job_id} not found. It may have expired or never existed.",
        )

    phase = status.get("phase")

    # Log completion or errors
    if phase == RefreshPhase.COMPLETED.value:
        logger.info(
            f"Refresh job {job_id} completed: {status.get('grants_saved')} grants saved"
        )
    elif phase == RefreshPhase.ERROR.value:
        logger.warning(f"Refresh job {job_id} failed: {status.get('error')}")

    return status
