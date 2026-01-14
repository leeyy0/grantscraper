from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ============================================================================
# SQLAlchemy Models (Database Schema)
# ============================================================================


class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    details = Column(Text, nullable=False)  # Use Text for long content

    # Relationships
    results = relationship("Result", back_populates="grant")


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    mission_and_focus = Column(Text, nullable=False)
    about_us = Column(Text, nullable=False)
    remarks = Column(Text, nullable=True)

    # Relationships
    initiatives = relationship("Initiative", back_populates="organisation")


class Initiative(Base):
    __tablename__ = "initiatives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    title = Column(String, nullable=False)
    goals = Column(Text, nullable=False)  # Objective of the initiative
    audience = Column(String, nullable=False)  # Target beneficiaries
    costs = Column(BigInteger, nullable=False)  # Estimated cost
    stage = Column(String, nullable=False)  # e.g., "concept", "expansion", "scaling"
    demographic = Column(String, nullable=True)  # Demographic of the team
    remarks = Column(Text, nullable=True)

    # Relationships
    organisation = relationship("Organisation", back_populates="initiatives")
    results = relationship("Result", back_populates="initiative")


class Result(Base):
    __tablename__ = "results"

    # Composite Primary Key
    grant_id = Column(Integer, ForeignKey("grants.id"), primary_key=True)
    initiative_id = Column(Integer, ForeignKey("initiatives.id"), primary_key=True)

    # Ratings & Analysis
    prelim_rating = Column(Integer, nullable=False)  # Out of 100
    grant_description = Column(Text, nullable=True)  # Summary of the grant
    criteria = Column(ARRAY(String), nullable=True)  # Eligibility criteria
    grant_amount = Column(
        String, nullable=True
    )  # Amount awarded (string for flexibility)
    match_rating = Column(Integer, nullable=True)  # Percentage (0-100)
    uncertainty_rating = Column(Integer, nullable=True)  # Percentage (0-100)
    deadline = Column(DateTime, nullable=True)  # Grant deadline
    sources = Column(ARRAY(String), nullable=True)  # URL links to grants

    # Explanations as JSON
    explanations = Column(JSON, nullable=True)
    # Expected structure:
    # {
    #   "match_rating": "string explaining match rating",
    #   "uncertainty_rating": "string explaining uncertainty"
    # }

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "prelim_rating >= 0 AND prelim_rating <= 100", name="check_prelim_rating"
        ),
        CheckConstraint(
            "match_rating >= 0 AND match_rating <= 100", name="check_match_rating"
        ),
        CheckConstraint(
            "uncertainty_rating >= 0 AND uncertainty_rating <= 100",
            name="check_uncertainty_rating",
        ),
    )

    # Relationships
    grant = relationship("Grant", back_populates="results")
    initiative = relationship("Initiative", back_populates="results")
