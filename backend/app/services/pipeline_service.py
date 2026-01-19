"""Service for running the grant filtering pipeline."""

import logging
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.access import (
    GrantAccess,
    InitiativeAccess,
    OrganisationAccess,
    ResultAccess,
    get_db_session,
)
from app.models.gemini import gemini_to_sqlalchemy
from app.models.models import Result
from app.services.deep_scraper import deep_scrape_grants
from app.services.file_service import download_files_from_links
from app.services.gemini_service import (
    analyze_grant_detailed,
    analyze_grant_preliminary,
)
from app.services.pipeline_status import PipelinePhase, update_status

logger = logging.getLogger(__name__)

# File structure paths
BASE_DIR = Path(__file__).parent.parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DEEP_SCRAPE_DIR = DOWNLOADS_DIR / "deep_scrape"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
DEEP_SCRAPE_DIR.mkdir(parents=True, exist_ok=True)

# Threshold for filtering grants in Phase 2
RATING_THRESHOLD = 61


def run_pipeline(initiative_id: int, threshold: int = RATING_THRESHOLD) -> None:
    """
    Run the complete grant filtering pipeline using standard Gemini API calls.
    """
    logger.info(
        f"Starting pipeline for initiative {initiative_id} with threshold {threshold}"
    )

    try:
        with get_db_session() as db:
            # Step 1: Read initiative and organization
            logger.info(f"Loading initiative {initiative_id} and organization...")
            initiative = InitiativeAccess.get_by_id(db, initiative_id)
            if not initiative:
                error_msg = f"Initiative {initiative_id} not found"
                logger.error(error_msg)
                update_status(initiative_id, PipelinePhase.ERROR, error=error_msg)
                return

            org = OrganisationAccess.get_by_id(db, initiative.organisation_id)
            if not org:
                error_msg = f"Organization for initiative {initiative_id} not found"
                logger.error(error_msg)
                update_status(initiative_id, PipelinePhase.ERROR, error=error_msg)
                return

            logger.info(f"Loaded organization: {org.name}")

            # Context Dicts
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
            logger.info("Loading all grants from database...")
            grants = GrantAccess.get_all(db)
            if not grants:
                error_msg = "No grants found in database"
                logger.error(error_msg)
                update_status(initiative_id, PipelinePhase.ERROR, error=error_msg)
                return

            logger.info(
                f"Processing {len(grants)} grants for initiative {initiative_id}"
            )

            # =================================================================
            # Step 3: Phase 1 - Preliminary ratings (STANDARD API CALLS)
            # =================================================================
            logger.info("Phase 1: Starting Preliminary Analysis...")
            update_status(
                initiative_id,
                PipelinePhase.PHASE_1_CALCULATING,
                remaining_calls=len(grants),
            )

            for idx, grant in enumerate(grants):
                logger.info(
                    f"Preliminary analysis {idx + 1}/{len(grants)}: {grant.name} (ID: {grant.id})"
                )

                grant_info_dict = {
                    "id": grant.id,
                    "name": grant.name,
                    "issuer": grant.issuer,
                    "url": grant.url,
                    "card_body_text": grant.card_body_text,
                }

                # Call Gemini API for preliminary rating
                prelim_rating = analyze_grant_preliminary(
                    grant_info_dict, org_info, initiative_info
                )

                logger.info(f"Grant {grant.id} preliminary rating: {prelim_rating}")

                # Save/Update Result
                result = ResultAccess.get_by_ids(db, grant.id, initiative_id)
                if result:
                    result.prelim_rating = prelim_rating
                    ResultAccess.update(db, result)
                else:
                    result = Result(
                        grant_id=grant.id,
                        initiative_id=initiative_id,
                        prelim_rating=prelim_rating,
                    )
                    ResultAccess.create(db, result)

                # Update status
                update_status(
                    initiative_id,
                    PipelinePhase.PHASE_1_CALCULATING,
                    remaining_calls=len(grants) - idx - 1,
                    total_grants=len(grants),
                    current_grant=idx + 1,
                )

            logger.info("Phase 1 completed: All preliminary ratings saved.")
            # =================================================================

            # Step 4: Filter grants above threshold
            logger.info(f"Filtering grants above threshold {threshold}...")
            filtered_results = ResultAccess.get_filtered_by_rating(
                db, initiative_id, threshold
            )

            filtered_grant_ids = [r.grant_id for r in filtered_results]
            filtered_grants = GrantAccess.get_by_ids(db, filtered_grant_ids)

            logger.info(
                f"Found {len(filtered_grants)} grants above threshold {threshold}"
            )

            if not filtered_grants:
                logger.info("No grants above threshold. Pipeline completed.")
                update_status(
                    initiative_id,
                    PipelinePhase.COMPLETED,
                    remaining_calls=0,
                    total_grants=len(grants),
                )
                return

            # Step 5: Phase 2 - Deep scraping
            logger.info("Phase 2: Starting deep scraping...")
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
                logger.info(f"Deep scraping {len(grant_dicts)} grants (max_depth=2)...")
                deep_scraped = deep_scrape_grants(page, grant_dicts, max_depth=2)

                browser.close()

            logger.info("Phase 2: Deep scraping completed")

            # Step 6: Download files and analyze with Gemini
            logger.info("Phase 2: Starting detailed analysis with Gemini...")
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
                    logger.info(
                        f"Analyzing grant {idx + 1}/{len(filtered_grants)}: "
                        f"{grant.name} (ID: {grant.id})"
                    )

                    # Download files to deep_scrape/grant_{id}/ directory
                    grant_dir = DEEP_SCRAPE_DIR / f"grant_{grant.id}"
                    grant_dir.mkdir(parents=True, exist_ok=True)

                    # Get links from deep scraped data
                    all_links = deep_data.get("links", [])
                    # Also get links from nested content
                    for nested in deep_data.get("deep_content", []):
                        all_links.extend(nested.get("links", []))

                    logger.debug(
                        f"Downloading {len(all_links)} files for grant {grant.id}..."
                    )

                    # Download files (converts docx to pdf automatically)
                    downloaded_files = download_files_from_links(
                        page, all_links, grant_dir, grant.id
                    )

                    logger.debug(f"Downloaded {len(downloaded_files)} files")

                    # Prepare grant info
                    grant_info = {
                        "id": grant.id,
                        "name": grant.name,
                        "issuer": grant.issuer,
                        "url": grant.url,
                        "card_body_text": grant.card_body_text,
                    }

                    # Get preliminary rating (Already in DB from Phase 1)
                    result = ResultAccess.get_by_ids(db, grant.id, initiative_id)
                    prelim_rating = result.prelim_rating if result else 50

                    logger.debug(
                        f"Sending grant {grant.id} to Gemini for detailed analysis..."
                    )

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
                    ResultAccess.create_or_update(db, result_obj)

                    logger.info(
                        f"Completed analysis for grant {grant.id}: "
                        f"Match Rating: {result_obj.match_rating}%, "
                        f"Uncertainty: {result_obj.uncertainty_rating}%"
                    )

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
            logger.info(
                f"Pipeline completed successfully for initiative {initiative_id}. "
                f"Processed {len(grants)} total grants, analyzed {len(filtered_grants)} in detail."
            )
            update_status(
                initiative_id,
                PipelinePhase.COMPLETED,
                remaining_calls=0,
                total_grants=len(grants),
            )

    except Exception as e:
        # Logs the full stack trace automatically via exc_info=True
        logger.error(
            f"Error in pipeline for initiative {initiative_id}: {e}", exc_info=True
        )
        update_status(
            initiative_id,
            PipelinePhase.ERROR,
            error=str(e),
        )
