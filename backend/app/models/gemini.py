from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from .models import Result

# ============================================================================
# Pydantic Models for Gemini Structured Output
# ============================================================================


class GeminiGrantAnalysis(BaseModel):
    """
    Schema for Gemini to return structured grant analysis.
    Note: grant_id, initiative_id, and prelim_rating are excluded from this schema
    to prevent LLM hallucinations. These fields should be provided separately when
    converting to Result objects.
    """

    grant_description: str = Field(
        description="Concise summary of what the grant is for and who it targets"
    )

    criteria: list[str] = Field(
        description="List of eligibility criteria extracted from the grant"
    )

    grant_amount: str = Field(
        description="Amount awarded by the grant (e.g., 'Up to $50,000' or 'Variable')"
    )

    match_rating: int = Field(
        ge=0,
        le=100,
        description="Match quality percentage between initiative goals and grant intent",
    )

    uncertainty_rating: int = Field(
        ge=0,
        le=100,
        description="Percentage indicating uncertainty due to missing information",
    )

    deadline: datetime | None = Field(
        None, description="Application deadline in ISO format if available"
    )

    sources: list[HttpUrl] = Field(
        description="URLs to the original grant pages for verification"
    )

    match_rating_explanation: str = Field(
        description="Detailed explanation of why this match rating was given, including alignment points and gaps"
    )

    uncertainty_rating_explanation: str = Field(
        description="Explanation of what information is missing or unclear that contributes to uncertainty"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "grant_description": "Supports technology adoption for eldercare services",
                "criteria": [
                    "Registered charity or IPC",
                    "Focus on elderly care",
                    "Technology implementation project",
                ],
                "grant_amount": "Up to $100,000",
                "match_rating": 82,
                "uncertainty_rating": 15,
                "deadline": "2026-03-31T23:59:59",
                "sources": ["https://oursg.gov.sg/grant/example"],
                "match_rating_explanation": "Strong alignment with initiative's goal of digital literacy for seniors. Grant explicitly supports tech adoption in eldercare. Minor gap: grant emphasizes hardware while initiative focuses on training.",
                "uncertainty_rating_explanation": "Grant description lacks detail on eligible training costs versus equipment costs. Unclear if capacity-building activities are covered.",
            }
        }


class GeminiBatchAnalysis(BaseModel):
    """
    Wrapper for analyzing multiple grants against one initiative.
    """

    initiative_id: int
    analyses: list[GeminiGrantAnalysis]


# ============================================================================
# Helper Functions for Conversion
# ============================================================================


def gemini_to_sqlalchemy(
    gemini_result: GeminiGrantAnalysis,
    grant_id: int,
    initiative_id: int,
    prelim_rating: int,
) -> Result:
    """
    Convert Gemini structured output to SQLAlchemy Result model.

    Args:
        gemini_result: The structured output from Gemini
        grant_id: ID of the grant being analyzed (provided separately)
        initiative_id: ID of the initiative being matched (provided separately)
        prelim_rating: Preliminary rating out of 100 (provided separately)
    """
    return Result(
        grant_id=grant_id,
        initiative_id=initiative_id,
        prelim_rating=prelim_rating,
        grant_description=gemini_result.grant_description,
        criteria=gemini_result.criteria,
        grant_amount=gemini_result.grant_amount,
        match_rating=gemini_result.match_rating,
        uncertainty_rating=gemini_result.uncertainty_rating,
        deadline=gemini_result.deadline,
        sources=[
            str(url) for url in gemini_result.sources
        ],  # Convert HttpUrl to string
        explanations={
            "match_rating": gemini_result.match_rating_explanation,
            "uncertainty_rating": gemini_result.uncertainty_rating_explanation,
        },
    )


def sqlalchemy_to_dict(result: Result) -> dict:
    """
    Convert SQLAlchemy Result to dictionary for API responses.
    """
    return {
        "grant_id": result.grant_id,
        "initiative_id": result.initiative_id,
        "prelim_rating": result.prelim_rating,
        "grant_description": result.grant_description,
        "criteria": result.criteria,
        "grant_amount": result.grant_amount,
        "match_rating": result.match_rating,
        "uncertainty_rating": result.uncertainty_rating,
        "deadline": result.deadline.isoformat() if result.deadline else None,
        "sources": result.sources,
        "explanations": result.explanations,
        "grant_name": result.grant.name,
        "grant_url": result.grant.url,
    }
