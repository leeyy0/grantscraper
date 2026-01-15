"""Status tracking for the grant filtering pipeline."""

from enum import Enum
from typing import Any

# Global status storage (in production, use Redis or database)
_pipeline_status: dict[int, dict[str, Any]] = {}


class PipelinePhase(Enum):
    """Pipeline phases."""

    IDLE = "idle"
    PHASE_1_CALCULATING = "calculating"  # Phase 1: Preliminary ratings
    PHASE_2_DEEP_SCRAPING = "deep_scraping"  # Phase 2: Deep scraping
    PHASE_2_ANALYZING = "analyzing"  # Phase 2: Gemini analysis
    COMPLETED = "completed"
    ERROR = "error"


def set_status(initiative_id: int, status: dict[str, Any]) -> None:
    """Set status for an initiative's pipeline."""
    _pipeline_status[initiative_id] = status


def get_status(initiative_id: int) -> dict[str, Any] | None:
    """Get status for an initiative's pipeline."""
    return _pipeline_status.get(initiative_id)


def update_status(
    initiative_id: int,
    phase: PipelinePhase,
    remaining_calls: int | None = None,
    total_grants: int | None = None,
    current_grant: int | None = None,
    error: str | None = None,
) -> None:
    """Update pipeline status."""
    status = {
        "phase": phase.value,
        "remaining_calls": remaining_calls,
        "total_grants": total_grants,
        "current_grant": current_grant,
        "error": error,
    }
    set_status(initiative_id, status)


def clear_status(initiative_id: int) -> None:
    """Clear status for an initiative."""
    if initiative_id in _pipeline_status:
        del _pipeline_status[initiative_id]
