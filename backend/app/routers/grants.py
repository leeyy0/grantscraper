"""Grant management endpoints for scraping and refreshing grant data."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

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
    Refresh the grants database by scraping the latest open grants.

    This endpoint:
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
        Summary of the refresh operation including:
        - total_found: Number of open grants found
        - grants_saved: Number of grants saved/updated in database
        - grant_urls: List of processed grant URLs
        - errors: Any errors encountered
    """
    logger.info(
        f"Starting grant refresh process (headless={headless}, "
        f"screenshots={take_screenshots})"
    )

    try:
        # Run scraping in a background thread to avoid blocking
        logger.info("Launching scraper in background thread...")
        result = await asyncio.to_thread(
            scrape_and_refresh_grants,
            take_screenshots=take_screenshots,
            headless=headless,
            save_to_db=True,
        )

        logger.info(
            f"Scraper completed. Found: {result['total_found']}, "
            f"Saved: {result['grants_saved']}, Errors: {len(result['errors'])}"
        )

        if result["errors"]:
            logger.warning(
                f"Grant refresh completed with {len(result['errors'])} error(s): "
                f"{result['errors']}"
            )
            return {
                "status": "completed_with_errors",
                "message": "Grant refresh completed but encountered some errors",
                **result,
            }

        logger.info(
            f"Grant refresh completed successfully. "
            f"Found {result['total_found']} grants, saved {result['grants_saved']} to database."
        )

        return {
            "status": "success",
            "message": f"Successfully refreshed {result['grants_saved']} grants",
            **result,
        }

    except Exception as e:
        logger.error(f"Error during grant refresh: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh grants: {str(e)}",
        )
