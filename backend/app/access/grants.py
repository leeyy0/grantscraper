"""CRUD operations for Grant model."""

from sqlalchemy.orm import Session

from app.models.models import Grant


class GrantAccess:
    """Access layer for Grant CRUD operations."""

    @staticmethod
    def get_by_id(db: Session, grant_id: int) -> Grant | None:
        """Get a grant by ID."""
        return db.query(Grant).filter(Grant.id == grant_id).first()

    @staticmethod
    def get_by_url(db: Session, url: str) -> Grant | None:
        """Get a grant by URL."""
        return db.query(Grant).filter(Grant.url == url).first()

    @staticmethod
    def get_all(db: Session) -> list[Grant]:
        """Get all grants."""
        return db.query(Grant).all()

    @staticmethod
    def get_by_ids(db: Session, grant_ids: list[int]) -> list[Grant]:
        """Get grants by a list of IDs."""
        return db.query(Grant).filter(Grant.id.in_(grant_ids)).all()

    @staticmethod
    def create(db: Session, grant: Grant) -> Grant:
        """Create a new grant."""
        db.add(grant)
        db.commit()
        db.refresh(grant)
        return grant

    @staticmethod
    def create_or_update_by_url(db: Session, grant: Grant) -> Grant:
        """Create a grant or update if it exists (matched by URL)."""
        existing = GrantAccess.get_by_url(db, grant.url)
        if existing:
            # Update existing grant
            for key, value in grant.__dict__.items():
                if not key.startswith("_") and key != "id":
                    setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new grant
            return GrantAccess.create(db, grant)

    @staticmethod
    def create_many(db: Session, grants: list[Grant]) -> list[Grant]:
        """Create multiple grants."""
        db.add_all(grants)
        db.commit()
        for grant in grants:
            db.refresh(grant)
        return grants

    @staticmethod
    def create_or_update_many_by_url(db: Session, grants: list[Grant]) -> list[Grant]:
        """Create or update multiple grants (matched by URL)."""
        result = []
        for grant in grants:
            result.append(GrantAccess.create_or_update_by_url(db, grant))
        return result

    @staticmethod
    def update(db: Session, grant: Grant) -> Grant:
        """Update an existing grant."""
        db.commit()
        db.refresh(grant)
        return grant

    @staticmethod
    def delete(db: Session, grant_id: int) -> bool:
        """Delete a grant by ID."""
        grant = GrantAccess.get_by_id(db, grant_id)
        if grant:
            db.delete(grant)
            db.commit()
            return True
        return False
