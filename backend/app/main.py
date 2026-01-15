"""FastAPI application for grant filtering pipeline."""

import asyncio
import json
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config.config import DB_URL
from app.models.gemini import gemini_to_sqlalchemy
from app.models.models import Grant, Initiative, Organisation, Result
from app.services.deep_scraper import deep_scrape_grants
from app.services.file_service import download_files_from_links
from app.services.gemini_service import (
    analyze_grant_detailed,
    analyze_grant_preliminary,
)
from app.services.pipeline_status import (
    PipelinePhase,
    clear_status,
    get_status,
    update_status,
)

# Initialize FastAPI app
app = FastAPI(title="Grant Scraper API", version="1.0.0")

# Database setup
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# File structure paths
BASE_DIR = Path(__file__).parent.parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
INITIAL_SCRAPE_DIR = DOWNLOADS_DIR / "initial_scrape"
DEEP_SCRAPE_DIR = DOWNLOADS_DIR / "deep_scrape"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
INITIAL_SCRAPE_DIR.mkdir(parents=True, exist_ok=True)
DEEP_SCRAPE_DIR.mkdir(parents=True, exist_ok=True)

# Threshold for filtering grants in Phase 2
RATING_THRESHOLD = 50  # Can be made configurable


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_pipeline(initiative_id: int, threshold: int = RATING_THRESHOLD) -> None:
    """
    Run the complete grant filtering pipeline.

    Steps:
    1. Read initiative from DB
    2. Get all grants from DB
    3. Phase 1: Calculate preliminary ratings
    4. Phase 2: Deep scrape and analyze grants above threshold
    5. Save results to DB
    """
    db = SessionLocal()
    try:
        # Step 1: Read initiative and organization
        initiative = db.query(Initiative).filter(Initiative.id == initiative_id).first()
        if not initiative:
            update_status(
                initiative_id,
                PipelinePhase.ERROR,
                error=f"Initiative {initiative_id} not found",
            )
            return

        org = (
            db.query(Organisation)
            .filter(Organisation.id == initiative.organisation_id)
            .first()
        )
        if not org:
            update_status(
                initiative_id,
                PipelinePhase.ERROR,
                error=f"Organization for initiative {initiative_id} not found",
            )
            return

        # Convert to dicts for easier handling
        org_info = {
            "id": org.id,
            "name": org.name,
            "mission_and_focus": org.mission_and_focus,
            "about_us": org.about_us,
            "remarks": org.remarks,
        }

        initiative_info = {
            "id": initiative.id,
            "title": initiative.title,
            "goals": initiative.goals,
            "audience": initiative.audience,
            "costs": initiative.costs,
            "stage": initiative.stage,
            "demographic": initiative.demographic,
            "remarks": initiative.remarks,
        }

        # Step 2: Get all grants
        grants = db.query(Grant).all()
        if not grants:
            update_status(
                initiative_id,
                PipelinePhase.ERROR,
                error="No grants found in database",
            )
            return

        print(f"Processing {len(grants)} grants for initiative {initiative_id}")

        # Step 3: Phase 1 - Preliminary ratings
        update_status(
            initiative_id,
            PipelinePhase.PHASE_1_CALCULATING,
            remaining_calls=len(grants),
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for idx, grant in enumerate(grants):
                grant_info = {
                    "id": grant.id,
                    "name": grant.name,
                    "url": grant.url,
                    "card_body_text": grant.card_body_text,
                    "details": grant.details,
                }

                # Calculate preliminary rating
                prelim_rating = analyze_grant_preliminary(
                    grant_info, org_info, initiative_info
                )

                # Save or update Result with preliminary rating
                result = (
                    db.query(Result)
                    .filter(
                        Result.grant_id == grant.id,
                        Result.initiative_id == initiative_id,
                    )
                    .first()
                )

                if result:
                    result.prelim_rating = prelim_rating
                else:
                    result = Result(
                        grant_id=grant.id,
                        initiative_id=initiative_id,
                        prelim_rating=prelim_rating,
                    )
                    db.add(result)

                db.commit()

                # Update status
                update_status(
                    initiative_id,
                    PipelinePhase.PHASE_1_CALCULATING,
                    remaining_calls=len(grants) - idx - 1,
                )

            browser.close()

        # Step 4: Filter grants above threshold
        filtered_results = (
            db.query(Result)
            .filter(
                Result.initiative_id == initiative_id,
                Result.prelim_rating > threshold,
            )
            .all()
        )

        filtered_grant_ids = [r.grant_id for r in filtered_results]
        filtered_grants = db.query(Grant).filter(Grant.id.in_(filtered_grant_ids)).all()

        print(f"Found {len(filtered_grants)} grants above threshold {threshold}")

        if not filtered_grants:
            update_status(
                initiative_id,
                PipelinePhase.COMPLETED,
                remaining_calls=0,
                total_grants=len(grants),
            )
            return

        # Step 5: Phase 2 - Deep scraping
        update_status(
            initiative_id,
            PipelinePhase.PHASE_2_DEEP_SCRAPING,
            remaining_calls=len(filtered_grants),
            total_grants=len(filtered_grants),
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Convert grants to dict format for deep scraper
            grant_dicts = []
            for grant in filtered_grants:
                grant_dicts.append(
                    {
                        "url": grant.url,
                        "button_text": grant.button_text or grant.name,
                        "card_body_text": grant.card_body_text,
                        "links": grant.links or [],
                    }
                )

            # Deep scrape
            deep_scraped = deep_scrape_grants(page, grant_dicts, max_depth=2)

            browser.close()

        # Step 6: Download files and analyze with Gemini
        update_status(
            initiative_id,
            PipelinePhase.PHASE_2_ANALYZING,
            remaining_calls=len(filtered_grants),
            total_grants=len(filtered_grants),
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for idx, (grant, deep_data) in enumerate(
                zip(filtered_grants, deep_scraped)
            ):
                # Download files
                grant_dir = DEEP_SCRAPE_DIR / f"grant_{grant.id}"
                grant_dir.mkdir(parents=True, exist_ok=True)

                # Get links from deep scraped data
                all_links = deep_data.get("links", [])
                # Also get links from nested content
                for nested in deep_data.get("deep_content", []):
                    all_links.extend(nested.get("links", []))

                # Download files
                downloaded_files = download_files_from_links(
                    page, all_links, grant_dir, grant.id
                )

                # Prepare grant info
                grant_info = {
                    "id": grant.id,
                    "name": grant.name,
                    "url": grant.url,
                    "card_body_text": grant.card_body_text,
                    "details": grant.details,
                }

                # Get preliminary rating
                result = (
                    db.query(Result)
                    .filter(
                        Result.grant_id == grant.id,
                        Result.initiative_id == initiative_id,
                    )
                    .first()
                )
                prelim_rating = result.prelim_rating if result else 50

                # Analyze with Gemini (with files)
                gemini_result = analyze_grant_detailed(
                    grant_info,
                    org_info,
                    initiative_info,
                    file_paths=downloaded_files if downloaded_files else None,
                )

                # Convert to Result and save
                result_obj = gemini_to_sqlalchemy(
                    gemini_result, grant.id, initiative_id, prelim_rating
                )

                # Update or create result
                existing_result = (
                    db.query(Result)
                    .filter(
                        Result.grant_id == grant.id,
                        Result.initiative_id == initiative_id,
                    )
                    .first()
                )

                if existing_result:
                    # Update existing result
                    for key, value in result_obj.__dict__.items():
                        if (
                            not key.startswith("_")
                            and key != "grant_id"
                            and key != "initiative_id"
                        ):
                            setattr(existing_result, key, value)
                else:
                    db.add(result_obj)

                db.commit()

                # Update status
                update_status(
                    initiative_id,
                    PipelinePhase.PHASE_2_ANALYZING,
                    remaining_calls=len(filtered_grants) - idx - 1,
                    total_grants=len(filtered_grants),
                    current_grant=idx + 1,
                )

            browser.close()

        # Step 7: Mark as completed
        update_status(
            initiative_id,
            PipelinePhase.COMPLETED,
            remaining_calls=0,
            total_grants=len(grants),
        )

    except Exception as e:
        print(f"Error in pipeline: {e}")
        update_status(
            initiative_id,
            PipelinePhase.ERROR,
            error=str(e),
        )
    finally:
        db.close()


@app.get("/filter-grants/{initiative_id}")
async def filter_grants(initiative_id: int, threshold: int = RATING_THRESHOLD):
    """
    Trigger the grant filtering pipeline for an initiative.

    This endpoint starts the pipeline asynchronously and returns immediately.
    Use /get-status to check progress.
    """
    # Check if initiative exists
    db = SessionLocal()
    try:
        initiative = db.query(Initiative).filter(Initiative.id == initiative_id).first()
        if not initiative:
            raise HTTPException(status_code=404, detail="Initiative not found")
    finally:
        db.close()

    # Clear any existing status
    clear_status(initiative_id)

    # Start pipeline in background
    asyncio.create_task(asyncio.to_thread(run_pipeline, initiative_id, threshold))

    return {
        "message": "Pipeline started",
        "initiative_id": initiative_id,
        "status_endpoint": "/get-status",
    }


@app.get("/get-status")
async def get_pipeline_status(initiative_id: int):
    """
    Get the current status of the pipeline for an initiative.

    Returns:
        - "calculating" during Phase 1
        - Number of grants during Phase 2 (preliminaryFilteredGrants.length)
        - Number of remaining calls during Phase 2 analysis
        - "completed" when done
    """
    status = get_status(initiative_id)

    if not status:
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
        return {
            "status": "error",
            "error": error,
        }

    if phase == PipelinePhase.PHASE_1_CALCULATING.value:
        return {
            "status": "calculating",
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.PHASE_2_DEEP_SCRAPING.value:
        return {
            "status": "deep_scraping",
            "total_grants": total_grants,
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.PHASE_2_ANALYZING.value:
        return {
            "status": "analyzing",
            "total_grants": total_grants,
            "current_grant": current_grant,
            "remaining_calls": remaining_calls,
        }

    if phase == PipelinePhase.COMPLETED.value:
        return {
            "status": "completed",
            "message": "Pipeline completed successfully",
            "total_grants": total_grants,
        }

    return {
        "status": phase,
        "remaining_calls": remaining_calls,
        "total_grants": total_grants,
    }


@app.get("/get-status-stream/{initiative_id}")
async def get_pipeline_status_stream(initiative_id: int):
    """
    Server-Sent Events stream for real-time pipeline status updates.

    Sends updates whenever the pipeline status changes.
    """

    async def event_generator():
        last_status = None
        while True:
            status = get_status(initiative_id)

            # Check if status changed
            if status != last_status:
                if status:
                    phase = status.get("phase", "idle")
                    if phase == PipelinePhase.COMPLETED.value:
                        yield f"data: {json.dumps({'status': 'completed', 'message': 'Pipeline completed successfully'})}\n\n"
                        break
                    elif phase == PipelinePhase.ERROR.value:
                        yield f"data: {json.dumps({'status': 'error', 'error': status.get('error')})}\n\n"
                        break
                    else:
                        yield f"data: {json.dumps(status)}\n\n"
                else:
                    yield f"data: {json.dumps({'status': 'idle'})}\n\n"

                last_status = status

            await asyncio.sleep(1)  # Check every second

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/results/{initiative_id}")
async def get_results(initiative_id: int, db: Session = Depends(get_db)):
    """Get all results for an initiative."""
    from app.models.gemini import sqlalchemy_to_dict

    results = db.query(Result).filter(Result.initiative_id == initiative_id).all()

    return {
        "initiative_id": initiative_id,
        "count": len(results),
        "results": [sqlalchemy_to_dict(r) for r in results],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
