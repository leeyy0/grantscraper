"""Pipeline endpoints for grant filtering operations."""

import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.access import InitiativeAccess, get_db_session
from app.services.pipeline_service import RATING_THRESHOLD, run_pipeline
from app.services.pipeline_status import (
    PipelinePhase,
    clear_status,
    get_status,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/filter-grants/{initiative_id}")
async def filter_grants(initiative_id: int, threshold: int = RATING_THRESHOLD):
    """
    Trigger the grant filtering pipeline for an initiative.

    This endpoint starts the pipeline asynchronously and returns immediately.
    Use /get-status to check progress.

    Args:
        initiative_id: ID of the initiative to filter grants for
        threshold: Minimum preliminary rating to include in deep analysis (default: 50)

    Returns:
        Confirmation message with status endpoint information
    """
    logger.info(
        f"Received request to filter grants for initiative {initiative_id} "
        f"with threshold {threshold}"
    )

    # Check if initiative exists
    with get_db_session() as db:
        initiative = InitiativeAccess.get_by_id(db, initiative_id)
        if not initiative:
            logger.warning(f"Initiative {initiative_id} not found")
            raise HTTPException(status_code=404, detail="Initiative not found")

    logger.info(f"Initiative {initiative_id} found. Clearing any existing status...")

    # Clear any existing status
    clear_status(initiative_id)

    # Start pipeline in background
    logger.info(f"Starting pipeline in background for initiative {initiative_id}...")
    asyncio.create_task(asyncio.to_thread(run_pipeline, initiative_id, threshold))

    logger.info(f"Pipeline task created for initiative {initiative_id}")

    return {
        "message": "Pipeline started",
        "initiative_id": initiative_id,
        "threshold": threshold,
        "status_endpoint": f"/pipeline/get-status?initiative_id={initiative_id}",
    }


@router.get("/get-status")
async def get_pipeline_status(initiative_id: int):
    """
    Get the current status of the pipeline for an initiative.

    Args:
        initiative_id: ID of the initiative

    Returns:
        - "calculating" during Phase 1 with remaining_calls
        - "deep_scraping" during Phase 2 scraping with total_grants (preliminaryFilteredGrants.length)
        - "analyzing" during Phase 2 analysis with current_grant and remaining_calls
        - "completed" when done
        - "error" if there was an error
    """
    logger.debug(f"Status check for initiative {initiative_id}")

    status = get_status(initiative_id)

    if not status:
        logger.debug(f"No pipeline status found for initiative {initiative_id}")
        return {
            "status": "idle",
            "message": "No pipeline running for this initiative",
        }

    phase = status.get("phase", "idle")
    remaining_calls = status.get("remaining_calls")
    total_grants = status.get("total_grants")
    current_grant = status.get("current_grant")
    error = status.get("error")

    if error:
        logger.info(f"Pipeline error for initiative {initiative_id}: {error}")
        return {
            "status": "error",
            "error": error,
        }

    if phase == PipelinePhase.PHASE_1_CALCULATING.value:
        logger.debug(
            f"Initiative {initiative_id}: Phase 1 - {remaining_calls} calls remaining"
        )
        return {
            "status": "calculating",
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.PHASE_2_DEEP_SCRAPING.value:
        logger.debug(
            f"Initiative {initiative_id}: Phase 2 Deep Scraping - "
            f"{total_grants} grants total"
        )
        return {
            "status": "deep_scraping",
            "total_grants": total_grants,  # This is preliminaryFilteredGrants.length
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.PHASE_2_ANALYZING.value:
        logger.debug(
            f"Initiative {initiative_id}: Phase 2 Analyzing - "
            f"Grant {current_grant}/{total_grants}"
        )
        return {
            "status": "analyzing",
            "total_grants": total_grants,  # This is preliminaryFilteredGrants.length
            "current_grant": current_grant,  # Index of grant + 1
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.COMPLETED.value:
        logger.info(
            f"Pipeline completed for initiative {initiative_id}. "
            f"Total grants: {total_grants}"
        )
        return {
            "status": "completed",
            "message": "Pipeline completed successfully",
            "total_grants": total_grants,
        }

    logger.debug(f"Initiative {initiative_id}: Status - {phase}")
    return {
        "status": phase,
        "remaining_calls": remaining_calls,
        "total_grants": total_grants,
    }


@router.get("/get-status-stream/{initiative_id}")
async def get_pipeline_status_stream(initiative_id: int):
    """
    Server-Sent Events stream for real-time pipeline status updates.

    Sends updates whenever the pipeline status changes.
    When status is "completed", sends a SUCCESS message and closes the stream.

    Args:
        initiative_id: ID of the initiative

    Returns:
        Server-Sent Events stream with real-time status updates
    """
    logger.info(f"Starting SSE stream for initiative {initiative_id}")

    async def event_generator():
        last_status = None
        event_count = 0

        while True:
            status = get_status(initiative_id)

            # Check if status changed
            if status != last_status:
                event_count += 1
                logger.debug(
                    f"SSE event #{event_count} for initiative {initiative_id}: "
                    f"Status changed"
                )

                if status:
                    phase = status.get("phase", "idle")
                    if phase == PipelinePhase.COMPLETED.value:
                        logger.info(
                            f"Pipeline completed for initiative {initiative_id}. "
                            f"Closing SSE stream."
                        )
                        yield f"data: {json.dumps({'status': 'completed', 'message': 'Pipeline completed successfully'})}\n\n"
                        break
                    elif phase == PipelinePhase.ERROR.value:
                        logger.error(
                            f"Pipeline error for initiative {initiative_id}: "
                            f"{status.get('error')}. Closing SSE stream."
                        )
                        yield f"data: {json.dumps({'status': 'error', 'error': status.get('error')})}\n\n"
                        break
                    else:
                        # Format status for SSE
                        phase = status.get("phase", "idle")
                        remaining_calls = status.get("remaining_calls")
                        total_grants = status.get("total_grants")
                        current_grant = status.get("current_grant")

                        sse_data = {"status": phase}
                        if remaining_calls is not None:
                            sse_data["remaining_calls"] = remaining_calls
                        if total_grants is not None:
                            sse_data["total_grants"] = total_grants
                        if current_grant is not None:
                            sse_data["current_grant"] = current_grant

                        yield f"data: {json.dumps(sse_data)}\n\n"
                else:
                    yield f"data: {json.dumps({'status': 'idle'})}\n\n"

                last_status = status

            await asyncio.sleep(1)  # Check every second

    return StreamingResponse(event_generator(), media_type="text/event-stream")
