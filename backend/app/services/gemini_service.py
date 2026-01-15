"""Service for interacting with Google Gemini API."""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

from app.models.gemini import GeminiGrantAnalysis

load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

if genai:
    genai.configure(api_key=GEMINI_API_KEY)


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
    if not genai:
        raise ImportError("google-generativeai is not installed")

    model = genai.GenerativeModel("gemini-1.5-pro")

    prompt = f"""
You are analyzing grants to match them with initiatives. Given the following information:

ORGANIZATION:
{org_info.get("name", "N/A")}
Mission: {org_info.get("mission_and_focus", "N/A")}
About: {org_info.get("about_us", "N/A")}

INITIATIVE:
Title: {initiative_info.get("title", "N/A")}
Goals: {initiative_info.get("goals", "N/A")}
Audience: {initiative_info.get("audience", "N/A")}
Costs: {initiative_info.get("costs", "N/A")}
Stage: {initiative_info.get("stage", "N/A")}

GRANT:
Name: {grant_info.get("name", "N/A")}
URL: {grant_info.get("url", "N/A")}
Details:
{grant_info.get("card_body_text", grant_info.get("details", "N/A"))}

Based on the grant information, provide a preliminary match rating from 0-100.
This should be a quick assessment of how well the grant might match the initiative.
Return ONLY the integer rating (0-100), nothing else.
"""

    try:
        response = model.generate_content(prompt)
        rating_text = response.text.strip()
        # Extract number from response
        rating = int("".join(filter(str.isdigit, rating_text))[:3])
        return min(100, max(0, rating))
    except Exception as e:
        print(f"Error in preliminary analysis: {e}")
        return 50  # Default rating


def analyze_grant_detailed(
    grant_info: dict[str, Any],
    org_info: dict[str, Any],
    initiative_info: dict[str, Any],
    file_paths: list[Path] | None = None,
) -> GeminiGrantAnalysis:
    """
    Phase 2: Detailed analysis of grant with files, returning structured output.

    Args:
        grant_info: Dictionary with grant details
        org_info: Dictionary with organization details
        initiative_info: Dictionary with initiative details
        file_paths: List of paths to PDF/text files to analyze

    Returns:
        GeminiGrantAnalysis with structured results
    """
    if not genai:
        raise ImportError("google-generativeai is not installed")

    model = genai.GenerativeModel(
        "gemini-1.5-pro",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": GeminiGrantAnalysis,
        },
    )

    # Build content for analysis
    text_content = f"""
ORGANIZATION:
Name: {org_info.get("name", "N/A")}
Mission and Focus: {org_info.get("mission_and_focus", "N/A")}
About Us: {org_info.get("about_us", "N/A")}
Remarks: {org_info.get("remarks", "N/A")}

INITIATIVE:
Title: {initiative_info.get("title", "N/A")}
Goals: {initiative_info.get("goals", "N/A")}
Audience: {initiative_info.get("audience", "N/A")}
Estimated Costs: {initiative_info.get("costs", "N/A")}
Stage: {initiative_info.get("stage", "N/A")}
Demographic: {initiative_info.get("demographic", "N/A")}
Remarks: {initiative_info.get("remarks", "N/A")}

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
Analyze this grant in detail and provide a comprehensive match assessment with the initiative.

Provide:
1. A concise grant description
2. Eligibility criteria (as a list)
3. Grant amount information
4. Match rating (0-100) - how well the grant matches the initiative
5. Uncertainty rating (0-100) - how much information is missing or unclear
6. Application deadline if available
7. Source URLs for verification
8. Sponsor name - the name of the organization or entity sponsoring the grant
9. Sponsor description - description of the sponsor organization, its mission, and background
10. Detailed explanations for both ratings

Return the analysis in the structured JSON format.
"""

    parts.append(prompt)

    try:
        response = model.generate_content(parts)
        # Parse JSON response
        import json

        result_dict = json.loads(response.text)
        return GeminiGrantAnalysis(**result_dict)
    except Exception as e:
        print(f"Error in detailed analysis: {e}")
        # Return a default analysis on error
        return GeminiGrantAnalysis(
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
