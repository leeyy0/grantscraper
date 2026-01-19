"""Utility script to re-run analysis for a specific grant."""

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
from app.services.deep_scraper import deep_scrape_grants
from app.services.file_service import download_files_from_links
from app.services.gemini_service import (
    analyze_grant_detailed,
    analyze_grant_preliminary,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File structure paths
BASE_DIR = Path(__file__).parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
DEEP_SCRAPE_DIR = DOWNLOADS_DIR / "deep_scrape"

DEEP_SCRAPE_DIR.mkdir(parents=True, exist_ok=True)


def rerun_grant_analysis(grant_id: int, initiative_id: int, phase: str = "both"):
    """
    Re-run analysis for a specific grant.

    Args:
        grant_id: ID of the grant to analyze
        initiative_id: ID of the initiative to analyze against
        phase: "preliminary", "detailed", or "both" (default: "both")
    """
    logger.info(
        f"Re-running analysis for grant {grant_id} and initiative {initiative_id}"
    )

    with get_db_session() as db:
        # Load grant, initiative, and organization
        grant = GrantAccess.get_by_id(db, grant_id)
        if not grant:
            logger.error(f"Grant {grant_id} not found")
            return

        initiative = InitiativeAccess.get_by_id(db, initiative_id)
        if not initiative:
            logger.error(f"Initiative {initiative_id} not found")
            return

        org = OrganisationAccess.get_by_id(db, initiative.organisation_id)
        if not org:
            logger.error(f"Organization for initiative {initiative_id} not found")
            return

        # Prepare context dictionaries
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

        grant_info = {
            "id": grant.id,
            "name": grant.name,
            "url": grant.url,
            "card_body_text": grant.card_body_text,
            "details": grant.details,
        }

        # Phase 1: Preliminary Analysis
        prelim_rating = None
        if phase in ["preliminary", "both"]:
            logger.info(f"Running preliminary analysis for grant {grant_id}...")
            prelim_rating = analyze_grant_preliminary(
                grant_info, org_info, initiative_info
            )
            logger.info(f"Preliminary rating: {prelim_rating}")

            # Update database
            result = ResultAccess.get_by_ids(db, grant_id, initiative_id)
            if result:
                result.prelim_rating = prelim_rating
                ResultAccess.update(db, result)
            else:
                from app.models.models import Result

                result = Result(
                    grant_id=grant_id,
                    initiative_id=initiative_id,
                    prelim_rating=prelim_rating,
                )
                ResultAccess.create(db, result)

        # Phase 2: Detailed Analysis
        if phase in ["detailed", "both"]:
            logger.info(f"Running detailed analysis for grant {grant_id}...")

            # Get preliminary rating if not just calculated
            if prelim_rating is None:
                result = ResultAccess.get_by_ids(db, grant_id, initiative_id)
                prelim_rating = result.prelim_rating if result else 50

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Deep scrape
                grant_dict = {
                    "url": grant.url,
                    "button_text": grant.button_text or grant.name,
                    "card_body_text": grant.card_body_text,
                    "links": grant.links or [],
                }

                logger.info("Deep scraping grant...")
                deep_scraped = deep_scrape_grants(page, [grant_dict], max_depth=2)
                deep_data = deep_scraped[0] if deep_scraped else {}

                # Download files
                grant_dir = DEEP_SCRAPE_DIR / f"grant_{grant_id}"
                grant_dir.mkdir(parents=True, exist_ok=True)

                all_links = deep_data.get("links", [])
                for nested in deep_data.get("deep_content", []):
                    all_links.extend(nested.get("links", []))

                logger.info(f"Downloading {len(all_links)} files...")
                downloaded_files = download_files_from_links(
                    page, all_links, grant_dir, grant_id
                )

                logger.info(f"Downloaded {len(downloaded_files)} files")

                # Analyze with Gemini
                logger.info("Analyzing with Gemini...")
                gemini_result = analyze_grant_detailed(
                    grant_info,
                    org_info,
                    initiative_info,
                    file_paths=downloaded_files if downloaded_files else None,
                )

                # Save to database
                result_obj = gemini_to_sqlalchemy(
                    gemini_result, grant_id, initiative_id, prelim_rating
                )
                ResultAccess.create_or_update(db, result_obj)

                logger.info(
                    f"Detailed analysis complete:\n"
                    f"  Match Rating: {result_obj.match_rating}%\n"
                    f"  Uncertainty: {result_obj.uncertainty_rating}%\n"
                    f"  Grant Amount: {result_obj.grant_amount}\n"
                    f"  Deadline: {result_obj.deadline}"
                )

                browser.close()

        logger.info(f"Successfully completed re-analysis for grant {grant_id}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python rerun_single_grant.py <grant_id> <initiative_id> [phase]")
        print("  phase: 'preliminary', 'detailed', or 'both' (default: 'both')")
        print("\nExample: python rerun_single_grant.py 30 1 both")
        sys.exit(1)

    grant_id = int(sys.argv[1])
    initiative_id = int(sys.argv[2])
    phase = sys.argv[3] if len(sys.argv) > 3 else "both"

    if phase not in ["preliminary", "detailed", "both"]:
        print("Error: phase must be 'preliminary', 'detailed', or 'both'")
        sys.exit(1)

    rerun_grant_analysis(grant_id, initiative_id, phase)
