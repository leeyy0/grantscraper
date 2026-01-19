"""Status tracking for grant refresh operations."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

# Global status storage (in production, use Redis or database)
_refresh_status: dict[str, dict[str, Any]] = {}


class RefreshPhase(Enum):
    """Refresh operation phases."""

    IDLE = "idle"
    STARTING = "starting"
    NAVIGATING = "navigating"
    EXTRACTING_LINKS = "extracting_links"
    SCRAPING_DETAILS = "scraping_details"
    SAVING_TO_DB = "saving_to_db"
    COMPLETED = "completed"
    ERROR = "error"


def create_job_id() -> str:
    """Generate a unique job ID for a refresh operation."""
    return str(uuid.uuid4())


def set_refresh_status(job_id: str, status: dict[str, Any]) -> None:
    """Set status for a refresh job."""
    _refresh_status[job_id] = status


def get_refresh_status(job_id: str) -> dict[str, Any] | None:
    """Get status for a refresh job."""
    return _refresh_status.get(job_id)


def update_refresh_status(
    job_id: str,
    phase: RefreshPhase,
    total_found: int | None = None,
    current_grant: int | None = None,
    grants_saved: int | None = None,
    message: str | None = None,
    error: str | None = None,
) -> None:
    """Update refresh job status."""
    status = _refresh_status.get(job_id, {})

    # Build update dict with only non-None values to preserve existing data
    updates = {
        "job_id": job_id,
        "phase": phase.value,
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    # Only update fields that are explicitly provided (not None)
    if total_found is not None:
        updates["total_found"] = total_found
    if current_grant is not None:
        updates["current_grant"] = current_grant
    if grants_saved is not None:
        updates["grants_saved"] = grants_saved
    if message is not None:
        updates["message"] = message
    if error is not None:
        updates["error"] = error

    status.update(updates)
    set_refresh_status(job_id, status)


def complete_refresh(
    job_id: str,
    total_found: int,
    grants_saved: int,
    grant_urls: list[str],
    errors: list[str],
) -> None:
    """Mark refresh job as completed."""
    status = {
        "job_id": job_id,
        "phase": RefreshPhase.COMPLETED.value,
        "total_found": total_found,
        "grants_saved": grants_saved,
        "grant_urls": grant_urls,
        "errors": errors,
        "completed_at": datetime.utcnow().isoformat(),
    }
    set_refresh_status(job_id, status)


def clear_refresh_status(job_id: str) -> None:
    """Clear status for a refresh job."""
    if job_id in _refresh_status:
        del _refresh_status[job_id]
