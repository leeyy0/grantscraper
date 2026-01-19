"""Service for interacting with Google Gemini API."""

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from app.core.config import GEMINI_BILLING_TIER
from app.models.gemini import GeminiDeepAnalysis, GeminiPreliminaryAnalysis

# --- LOGGING SETUP START ---
log_dir = Path(".private")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger("gemini_debugger")
logger.setLevel(logging.DEBUG)
logger.propagate = False

log_file = open(log_dir / "gemini_debug.log", "a", encoding="utf-8", buffering=1)
file_handler = logging.StreamHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter("[GEMINI] %(message)s")
console_handler.setFormatter(console_formatter)

if not logger.hasHandlers():
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
# --- LOGGING SETUP END ---

# --- CONFIGURATION ---
# Use the specific environment variable requested
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("CRITICAL: GEMINI_API_KEY is missing from environment variables!")

client = genai.Client(api_key=api_key)

# The model to use
GEMINI_MODEL = "gemini-3-pro-preview"

# Rate limiting
if GEMINI_BILLING_TIER == "FREE":
    RATE_LIMIT_DELAY = 30
else:
    RATE_LIMIT_DELAY = 4.5

# Retry configuration
MAX_RETRIES = 7
RETRY_DELAY = 10  # seconds to wait between retries


def rate_limit_sleep():
    """Sleep to respect API rate limits."""
    time.sleep(RATE_LIMIT_DELAY)


# --- PRELIMINARY ANALYSIS (PHASE 1) ---


def analyze_grant_preliminary(
    grant_info: dict[str, Any],
    org_info: dict[str, Any],
    initiative_info: dict[str, Any],
) -> int:
    """
    Phase 1: Quick preliminary rating of grant relevance (0-100).
    Returns the rating as an integer.
    Retries up to MAX_RETRIES times on failure.
    """

    prompt = f"""Review this grant information against the following organisation and initiative:

ORGANISATION CONTEXT:
Name: {org_info.get("name", "N/A")}
Mission and Focus: {org_info.get("mission_and_focus", "N/A")}
About Us: {org_info.get("about_us", "N/A")}
{f"Additional Remarks: {org_info.get('remarks')}" if org_info.get("remarks") else ""}

INITIATIVE DETAILS:
Title: {initiative_info.get("title", "N/A")}
Goals: {initiative_info.get("goals", "N/A")}
Target Audience: {initiative_info.get("audience", "N/A")}
Stage: {initiative_info.get("stage", "N/A")}
Budget: ${initiative_info.get("costs") or 0:,}
{f"Demographic: {initiative_info.get('demographic')}" if initiative_info.get("demographic") else ""}
{f"Remarks: {initiative_info.get('remarks')}" if initiative_info.get("remarks") else ""}

GRANT INFORMATION:
Name: {grant_info.get("name", "N/A")}
URL: {grant_info.get("url", "N/A")}
Details:
{grant_info.get("card_body_text", grant_info.get("details", "N/A"))}

Rate the relevance of this grant to this specific initiative on a scale of 0-100, where:
- 0-20: Not relevant at all
- 21-40: Slightly relevant
- 41-60: Moderately relevant
- 61-80: Highly relevant
- 81-100: Extremely relevant

Consider:
1. PRIMARY REQUIREMENT: Direct alignment with the INITIATIVE. (Most Important)
   - Does this grant specifically fund the activities described in the Initiative's goals?
   - Is the grant amount appropriate for the Initiative's budget ($ {initiative_info.get("costs")})?

2. Demographic and Audience Fit.
   - Does the grant's target audience match the Initiative's audience ({initiative_info.get("audience")}) and demographic?

3. Organisation Alignment.
   - Does this fit within the broader mission of {org_info.get("name")}? (Use this only as a final "sanity check").
Return a JSON object with a single field 'rating' containing the integer score (0-100)."""

    logger.debug(f"--- PRELIMINARY PROMPT ---\n{prompt}\n--------------------------")

    # Retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": GeminiPreliminaryAnalysis.model_json_schema(),
                },
            )

            logger.debug(
                f"--- GEMINI RESPONSE (PRELIMINARY) ---\n{response.text}\n-------------------------------------"
            )
            analysis = GeminiPreliminaryAnalysis.model_validate_json(response.text)
            return analysis.rating

        except Exception as e:
            logger.error(
                f"Error in preliminary analysis for grant {grant_info.get('id')} (attempt {attempt}/{MAX_RETRIES}): {e}"
            )

            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(
                    f"All {MAX_RETRIES} attempts failed for grant {grant_info.get('id')}. Returning default rating of 50."
                )
                return 50  # Default to middle rating after all retries exhausted

        finally:
            # Only sleep for rate limiting if request was successful or it's not the last retry
            if attempt < MAX_RETRIES:
                rate_limit_sleep()

    # This should never be reached due to the return in the else block above, but just in case
    return 50


# --- DETAILED ANALYSIS (PHASE 2) ---


def analyze_grant_detailed(
    grant_info: dict[str, Any],
    org_info: dict[str, Any],
    initiative_info: dict[str, Any],
    file_paths: list[Path] | None = None,
) -> GeminiDeepAnalysis:
    """
    Phase 2: Detailed analysis of grant with files.
    Retries up to MAX_RETRIES times on failure.
    """

    text_content = f"""Analyze these comprehensive grant documents in detail for the following organisation and initiative:

ORGANISATION CONTEXT:
Name: {org_info.get("name", "N/A")}
Mission and Focus: {org_info.get("mission_and_focus", "N/A")}
About Us: {org_info.get("about_us", "N/A")}
{f"Additional Remarks: {org_info.get('remarks')}" if org_info.get("remarks") else ""}

INITIATIVE DETAILS:
Title: {initiative_info.get("title", "N/A")}
Goals: {initiative_info.get("goals", "N/A")}
Target Audience: {initiative_info.get("audience", "N/A")}
Stage: {initiative_info.get("stage", "N/A")}
Budget: ${initiative_info.get("costs") or 0:,}
{f"Demographic: {initiative_info.get('demographic')}" if initiative_info.get("demographic") else ""}
{f"Remarks: {initiative_info.get('remarks')}" if initiative_info.get("remarks") else ""}

GRANT BASIC INFORMATION:
Name: {grant_info.get("name", "N/A")}
URL: {grant_info.get("url", "N/A")}
Basic Details:
{grant_info.get("card_body_text", grant_info.get("details", "N/A"))}
"""

    parts = [text_content]
    if file_paths:
        for file_path in file_paths:
            if file_path.exists():
                file_size_mb = file_path.stat().st_size / (1024 * 1024)

                if file_path.suffix.lower() == ".pdf":
                    if file_size_mb <= 50:
                        parts.append(
                            types.Part.from_bytes(
                                data=file_path.read_bytes(),
                                mime_type="application/pdf",
                            )
                        )
                    else:
                        parts.append(genai.upload_file(str(file_path)))
                elif file_path.suffix.lower() in [".txt", ".md"]:
                    parts.append(file_path.read_text(encoding="utf-8"))

    prompt = """
Analyze this grant in detail and extract the following information:

1. Grant Description: Brief summary (2-3 sentences) of what the grant funds and who it targets
2. Eligibility Criteria: List all eligibility requirements found in the documents
3. Grant Amount: Funding amount or range (e.g., '$50,000 - $100,000' or 'Up to $250,000')
4. Match Rating: 0-100 score for overall match quality considering both organisation mission and initiative specifics
5. Uncertainty Rating: 0-100 score for confidence (higher = more uncertain/missing information)
6. Deadline: Application deadline if available
7. Sources: Where you found key information (page numbers, section names, or URLs)
8. Match Rating Explanation: Detailed explanation of how grant aligns with organisation mission and initiative goals
9. Uncertainty Rating Explanation: Explanation of what information is missing or unclear
10. Sponsor Name: Name of the organization or entity sponsoring the grant
11. Sponsor Description: Description of the sponsor organization, its mission, and background

Consider both the organisation's broader mission AND the specific initiative's needs when rating.
"""

    parts.append(prompt)
    logger.debug(
        f"--- DETAILED PROMPT (Files Hidden) ---\n{text_content}\n{prompt}\n--------------------------------------"
    )

    # Retry loop
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=parts,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": GeminiDeepAnalysis.model_json_schema(),
                },
            )

            logger.debug(
                f"--- GEMINI RESPONSE (DETAILED) ---\n{response.text}\n----------------------------------"
            )
            analysis = GeminiDeepAnalysis.model_validate_json(response.text)
            return analysis

        except Exception as e:
            logger.error(
                f"Error in detailed analysis for grant {grant_info.get('id')} (attempt {attempt}/{MAX_RETRIES}): {e}"
            )

            if attempt < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(
                    f"All {MAX_RETRIES} attempts failed for grant {grant_info.get('id')}. Returning error response."
                )
                return GeminiDeepAnalysis(
                    grant_description="Analysis error occurred after multiple retries",
                    criteria=[],
                    grant_amount="Unknown",
                    match_rating=0,
                    uncertainty_rating=100,
                    deadline=None,
                    sources=[grant_info.get("url", "")],
                    match_rating_explanation=f"Error during analysis after {MAX_RETRIES} attempts: {str(e)}",
                    uncertainty_rating_explanation="Unable to complete analysis due to repeated errors",
                    sponsor_name="Unknown",
                    sponsor_description="Unknown",
                )

        finally:
            # Only sleep for rate limiting if request was successful or it's not the last retry
            if attempt < MAX_RETRIES:
                rate_limit_sleep()

    # This should never be reached, but just in case
    return GeminiDeepAnalysis(
        grant_description="Analysis error occurred",
        criteria=[],
        grant_amount="Unknown",
        match_rating=0,
        uncertainty_rating=100,
        deadline=None,
        sources=[grant_info.get("url", "")],
        match_rating_explanation="Unexpected error in retry logic",
        uncertainty_rating_explanation="Unable to complete analysis",
        sponsor_name="Unknown",
        sponsor_description="Unknown",
    )
