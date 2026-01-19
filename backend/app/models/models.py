from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
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
    issuer = Column(Text, nullable=True)
    name = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    button_text = Column(Text, nullable=True)  # Button text from listing page
    card_body_text = Column(Text, nullable=True)  # Clean text content (for LLM)
    card_body_html = Column(Text, nullable=True)  # HTML content (if use_text=False)
    links = Column(ARRAY(Text), nullable=True)  # URLs found in card-body

    # Relationships
    results = relationship("Result", back_populates="grant")

    @classmethod
    def from_scraper_dict(cls, grant_dict: dict) -> "Grant":
        """Create a Grant instance from a dictionary returned by get_grant_details().

        Args:
            grant_dict: Dictionary with keys: url, button_text, card_body_text/card_body_html,
                       links, issuer, title

        Returns:
            Grant instance (not yet persisted to database)
        """
        # Use title as name (primary source), with fallbacks
        name = grant_dict.get("title")
        if not name:
            # Fallback 1: Use button_text
            name = grant_dict.get("button_text")
        if not name:
            # Fallback 2: extract grant ID from URL
            url_parts = grant_dict.get("url", "").split("/")
            if len(url_parts) >= 2:
                name = (
                    url_parts[-2] if url_parts[-1] == "instruction" else url_parts[-1]
                )
        if not name:
            # Fallback 3: Use a default value to ensure non-null
            name = "Unknown Grant"

        # Use issuer from scraper (can be None/null if not found)
        issuer = grant_dict.get("issuer") or None

        return cls(
            issuer=issuer,
            name=name,
            url=grant_dict.get("url"),
            button_text=grant_dict.get("button_text"),
            card_body_text=grant_dict.get("card_body_text"),
            card_body_html=grant_dict.get("card_body_html"),
            links=grant_dict.get("links", []),
        )


class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    mission_and_focus = Column(Text, nullable=False)
    about_us = Column(Text, nullable=False)
    remarks = Column(Text, nullable=True)

    # Relationships
    initiatives = relationship("Initiative", back_populates="organisation")


class Initiative(Base):
    __tablename__ = "initiatives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organisation_id = Column(Integer, ForeignKey("organisations.id"), nullable=False)
    title = Column(Text, nullable=False)
    goals = Column(Text, nullable=False)  # Objective of the initiative
    audience = Column(Text, nullable=False)  # Target beneficiaries
    costs = Column(BigInteger, nullable=True)  # Estimated cost
    stage = Column(Text, nullable=False)  # e.g., "concept", "expansion", "scaling"
    demographic = Column(Text, nullable=True)  # Demographic of the team
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
    criteria = Column(ARRAY(Text), nullable=True)  # Eligibility criteria
    grant_amount = Column(
        Text, nullable=True
    )  # Amount awarded (string for flexibility)
    match_rating = Column(Integer, nullable=True)  # Percentage (0-100)
    uncertainty_rating = Column(Integer, nullable=True)  # Percentage (0-100)
    deadline = Column(DateTime, nullable=True)  # Grant deadline
    sources = Column(ARRAY(Text), nullable=True)  # URL links to grants
    sponsor_name = Column(Text, nullable=True)  # Name of the grant sponsor
    sponsor_description = Column(Text, nullable=True)  # Description of the sponsor

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
