"""CRUD operations for Organisation model."""

from sqlalchemy.orm import Session

from app.models.models import Organisation


class OrganisationAccess:
    """Access layer for Organisation CRUD operations."""

    @staticmethod
    def get_by_id(db: Session, organisation_id: int) -> Organisation | None:
        """Get an organisation by ID."""
        return db.query(Organisation).filter(Organisation.id == organisation_id).first()

    @staticmethod
    def get_all(db: Session) -> list[Organisation]:
        """Get all organisations."""
        return db.query(Organisation).all()

    @staticmethod
    def create(db: Session, organisation: Organisation) -> Organisation:
        """Create a new organisation."""
        db.add(organisation)
        db.commit()
        db.refresh(organisation)
        return organisation

    @staticmethod
    def update(db: Session, organisation: Organisation) -> Organisation:
        """Update an existing organisation."""
        db.commit()
        db.refresh(organisation)
        return organisation

    @staticmethod
    def delete(db: Session, organisation_id: int) -> bool:
        """Delete an organisation by ID."""
        organisation = OrganisationAccess.get_by_id(db, organisation_id)
        if organisation:
            db.delete(organisation)
            db.commit()
            return True
        return False
