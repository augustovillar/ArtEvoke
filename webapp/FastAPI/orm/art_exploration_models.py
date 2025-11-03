"""
ORM models for Art Exploration functionality: ArtExploration and Images.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    ForeignKey,
    Enum,
    SmallInteger,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base
from api_types.common import Dataset, Language

class ArtExploration(Base):
    """ArtExploration table - stores art exploration sessions."""

    __tablename__ = "ArtExploration"
    __table_args__ = (
        Index("idx_artexp_patient", "patient_id"),
        Index("idx_artexp_session", "session_id"),
        Index("idx_artexp_dataset", "dataset"),
        Index("idx_artexp_language", "language"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    patient_id = Column(
        String(36),
        ForeignKey("Patient.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    session_id = Column(
        String(36),
        ForeignKey("Session.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    story_generated = Column(Text, nullable=True)  # Filled when patient completes session
    dataset = Column(
        Enum(Dataset, name="art_exploration_dataset"),
        nullable=True,  # Selected during session by patient
    )
    language = Column(
        Enum(Language, name="art_exploration_language"), 
        nullable=True  # Selected during session by patient
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="art_explorations")
    images = relationship(
        "Images", back_populates="art_exploration", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", 
        back_populates="art_exploration",
        foreign_keys="[Session.art_exploration_id]"
    )
    ae_questions = relationship(
        "AEQuestion", back_populates="art_exploration", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ArtExploration(id={self.id}, patient_id={self.patient_id}, dataset={self.dataset})>"


class Images(Base):
    """Images table - ordered list of images linked to an ArtExploration."""

    __tablename__ = "Images"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    art_exploration_id = Column(
        String(36),
        ForeignKey("ArtExploration.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    catalog_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    display_order = Column(SmallInteger, nullable=False)

    # Relationships
    art_exploration = relationship("ArtExploration", back_populates="images")
    catalog_item = relationship("CatalogItem", back_populates="images")

    def __repr__(self):
        return f"<Images(id={self.id}, art_exploration_id={self.art_exploration_id}, order={self.display_order})>"
