"""Results endpoints for retrieving grant filtering results."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.access import ResultAccess, get_db

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{initiative_id}")
async def get_results(initiative_id: int, db: Session = Depends(get_db)):
    """
    Get all results for an initiative.

    This endpoint retrieves all grant analysis results associated with
    a specific initiative, including preliminary ratings, match ratings,
    uncertainty ratings, and detailed analysis data.

    Args:
        initiative_id: ID of the initiative
        db: Database session (injected)

    Returns:
        Dictionary containing:
        - initiative_id: The initiative ID
        - count: Number of results
        - results: List of result objects with all analysis data
    """
    logger.info(f"Fetching results for initiative {initiative_id}")

    from app.models.gemini import sqlalchemy_to_dict

    results = ResultAccess.get_by_initiative_id(db, initiative_id)

    logger.info(f"Found {len(results)} results for initiative {initiative_id}")

    # Log summary statistics if results exist
    if results:
        avg_prelim = sum(r.prelim_rating for r in results) / len(results)
        match_ratings = [r.match_rating for r in results if r.match_rating is not None]
        avg_match = sum(match_ratings) / len(match_ratings) if match_ratings else 0

        logger.debug(
            f"Initiative {initiative_id} summary: "
            f"Avg preliminary rating: {avg_prelim:.1f}, "
            f"Avg match rating: {avg_match:.1f}, "
            f"Detailed results: {len(match_ratings)}/{len(results)}"
        )

    return {
        "initiative_id": initiative_id,
        "count": len(results),
        "results": [sqlalchemy_to_dict(r) for r in results],
    }
