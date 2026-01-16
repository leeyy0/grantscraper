"""CRUD operations for Initiative model."""

from sqlalchemy.orm import Session

from app.models.models import Initiative


class InitiativeAccess:
    """Access layer for Initiative CRUD operations."""

    @staticmethod
    def get_by_id(db: Session, initiative_id: int) -> Initiative | None:
        """Get an initiative by ID."""
        return db.query(Initiative).filter(Initiative.id == initiative_id).first()

    @staticmethod
    def get_by_organisation_id(db: Session, organisation_id: int) -> list[Initiative]:
        """Get all initiatives for an organisation."""
        return (
            db.query(Initiative)
            .filter(Initiative.organisation_id == organisation_id)
            .all()
        )

    @staticmethod
    def get_all(db: Session) -> list[Initiative]:
        """Get all initiatives."""
        return db.query(Initiative).all()

    @staticmethod
    def create(db: Session, initiative: Initiative) -> Initiative:
        """Create a new initiative."""
        db.add(initiative)
        db.commit()
        db.refresh(initiative)
        return initiative

    @staticmethod
    def update(db: Session, initiative: Initiative) -> Initiative:
        """Update an existing initiative."""
        db.commit()
        db.refresh(initiative)
        return initiative

    @staticmethod
    def delete(db: Session, initiative_id: int) -> bool:
        """Delete an initiative by ID."""
        initiative = InitiativeAccess.get_by_id(db, initiative_id)
        if initiative:
            db.delete(initiative)
            db.commit()
            return True
        return False
