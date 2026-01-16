"""CRUD operations for Result model."""

from sqlalchemy.orm import Session

from app.models.models import Result


class ResultAccess:
    """Access layer for Result CRUD operations."""

    @staticmethod
    def get_by_ids(db: Session, grant_id: int, initiative_id: int) -> Result | None:
        """Get a result by grant_id and initiative_id."""
        return (
            db.query(Result)
            .filter(
                Result.grant_id == grant_id,
                Result.initiative_id == initiative_id,
            )
            .first()
        )

    @staticmethod
    def get_by_initiative_id(db: Session, initiative_id: int) -> list[Result]:
        """Get all results for an initiative."""
        return db.query(Result).filter(Result.initiative_id == initiative_id).all()

    @staticmethod
    def get_by_grant_id(db: Session, grant_id: int) -> list[Result]:
        """Get all results for a grant."""
        return db.query(Result).filter(Result.grant_id == grant_id).all()

    @staticmethod
    def get_filtered_by_rating(
        db: Session, initiative_id: int, min_rating: int
    ) -> list[Result]:
        """Get results for an initiative with rating above threshold."""
        return (
            db.query(Result)
            .filter(
                Result.initiative_id == initiative_id,
                Result.prelim_rating > min_rating,
            )
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> list[Result]:
        """Get all results."""
        return db.query(Result).all()

    @staticmethod
    def create(db: Session, result: Result) -> Result:
        """Create a new result."""
        db.add(result)
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def create_or_update(db: Session, result: Result) -> Result:
        """Create a result or update if it exists."""
        existing = ResultAccess.get_by_ids(db, result.grant_id, result.initiative_id)
        if existing:
            # Update existing result
            for key, value in result.__dict__.items():
                if (
                    not key.startswith("_")
                    and key != "grant_id"
                    and key != "initiative_id"
                ):
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new result
            return ResultAccess.create(db, result)

    @staticmethod
    def update(db: Session, result: Result) -> Result:
        """Update an existing result."""
        db.commit()
        db.refresh(result)
        return result

    @staticmethod
    def delete(db: Session, grant_id: int, initiative_id: int) -> bool:
        """Delete a result by grant_id and initiative_id."""
        result = ResultAccess.get_by_ids(db, grant_id, initiative_id)
        if result:
            db.delete(result)
            db.commit()
            return True
        return False
