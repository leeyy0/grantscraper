"""Service for interacting with Google Gemini API."""

import os
import time
from pathlib import Path
from typing import Any

from google import genai

from app.core.config import GEMINI_API_KEY
from app.models.gemini import GeminiDeepAnalysis, GeminiPreliminaryAnalysis

# Set API key in environment for genai library
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

client = genai.Client()

GEMINI_MODEL = "gemini-3-flash-preview"

# Rate limiting configuration (15 requests per minute for free tier)
RATE_LIMIT_DELAY = 4.5  # seconds between requests (60/15 = 4, adding buffer)


def rate_limit_sleep():
    """Sleep to respect API rate limits."""
    time.sleep(RATE_LIMIT_DELAY)


def analyze_grant_preliminary(
    grant_info: dict[str, Any],
    org_info: dict[str, Any],
    initiative_info: dict[str, Any],
) -> int:
    """
    Phase 1: Analyze grant and return preliminary rating (0-100).

    Args:
        grant_info: Dictionary with grant details (name, url, card_body_text, etc.)
        org_info: Dictionary with organization details
        initiative_info: Dictionary with initiative details

    Returns:
        Preliminary rating (0-100)
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

Rate the relevance of this grant to the organisation's mission and this specific initiative on a scale of 0-100, where:
- 0-20: Not relevant at all
- 21-40: Slightly relevant
- 41-60: Moderately relevant
- 61-80: Highly relevant
- 81-100: Extremely relevant

Consider:
- Alignment with the organisation's overall mission and focus
- Fit with the initiative's specific goals and audience
- Appropriateness for the initiative's stage and budget
- Match with target demographic

Return ONLY the integer rating (0-100), nothing else."""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiPreliminaryAnalysis.model_json_schema(),
            },
        )
        rate_limit_sleep()  # Rate limit after API call

        # Parse the structured JSON response
        analysis = GeminiPreliminaryAnalysis.model_validate_json(response.text)
        return analysis.rating
    except Exception as e:
        print(f"Error in preliminary analysis: {e}")
        return 50  # Default rating


def analyze_grant_detailed(
    grant_info: dict[str, Any],
    org_info: dict[str, Any],
    initiative_info: dict[str, Any],
    file_paths: list[Path] | None = None,
) -> GeminiDeepAnalysis:
    """
    Phase 2: Detailed analysis of grant with files, returning structured output.

    Args:
        grant_info: Dictionary with grant details
        org_info: Dictionary with organization details
        initiative_info: Dictionary with initiative details
        file_paths: List of paths to PDF/text files to analyze

    Returns:
        GeminiDeepAnalysis with structured results
    """

    # Build content for analysis
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

    # Prepare file parts if files are provided
    parts = [text_content]
    if file_paths:
        for file_path in file_paths:
            if file_path.exists():
                if file_path.suffix.lower() == ".pdf":
                    parts.append(genai.upload_file(str(file_path)))
                elif file_path.suffix.lower() in [".txt", ".md"]:
                    parts.append(file_path.read_text(encoding="utf-8"))
                # Note: DOCX should be converted to PDF before calling this

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

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=parts,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": GeminiDeepAnalysis.model_json_schema(),
            },
        )
        rate_limit_sleep()  # Rate limit after API call

        # Parse the structured JSON response
        analysis = GeminiDeepAnalysis.model_validate_json(response.text)
        return analysis
    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        # Return a default analysis on error
        return GeminiDeepAnalysis(
            grant_description="Analysis error occurred",
            criteria=[],
            grant_amount="Unknown",
            match_rating=0,
            uncertainty_rating=100,
            deadline=None,
            sources=[grant_info.get("url", "")],
            match_rating_explanation=f"Error during analysis: {str(e)}",
            uncertainty_rating_explanation="Unable to complete analysis due to error",
            sponsor_name="Unknown",
            sponsor_description="Unable to determine sponsor information due to analysis error",
        )
