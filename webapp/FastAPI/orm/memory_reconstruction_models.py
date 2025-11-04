"""
ORM models for Memory Reconstruction functionality: MemoryReconstruction and Sections.
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
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base
from api_types.common import Dataset, Language, SegmentationStrategy

class MemoryReconstruction(Base):
    """MemoryReconstruction table - stores memory reconstruction sessions."""

    __tablename__ = "MemoryReconstruction"
    __table_args__ = (
        Index("idx_memrec_session", "session_id"),
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
    story = Column(Text, nullable=True)  # Filled when patient starts session
    dataset = Column(
        Enum(Dataset, name="memory_reconstruction_dataset"),
        nullable=True,  # Selected during session by patient
    )
    language = Column(
        Enum(Language, name="memory_reconstruction_language"), 
        nullable=True  # Selected during session by patient
    )
    segmentation_strategy = Column(
        Enum(SegmentationStrategy, name="segmentation_strategy"), 
        nullable=True  # Selected during session by patient
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="memory_reconstructions")
    sections = relationship(
        "Sections", back_populates="memory_reconstruction", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "Session", 
        back_populates="memory_reconstruction",
        foreign_keys="[Session.memory_reconstruction_id]"
    )
    mr_questions = relationship(
        "MRQuestion",
        back_populates="memory_reconstruction",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<MemoryReconstruction(id={self.id}, patient_id={self.patient_id}, strategy={self.segmentation_strategy})>"


class Sections(Base):
    """Sections table - story sections with up to 6 images plus a favorite."""

    __tablename__ = "Sections"
    __table_args__ = (
        Index("idx_sections_memrec", "memory_reconstruction_id"),
        UniqueConstraint(
            "memory_reconstruction_id", "display_order", name="uq_sections_memrec_order"
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    memory_reconstruction_id = Column(
        String(36),
        ForeignKey("MemoryReconstruction.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    section_content = Column(Text, nullable=False)
    display_order = Column(SmallInteger, nullable=False)
    image1_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    image2_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    image3_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    image4_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    image5_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    image6_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    fav_image_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    memory_reconstruction = relationship(
        "MemoryReconstruction", back_populates="sections"
    )
    image1 = relationship(
        "CatalogItem", foreign_keys=[image1_id], back_populates="sections_image1"
    )
    image2 = relationship(
        "CatalogItem", foreign_keys=[image2_id], back_populates="sections_image2"
    )
    image3 = relationship(
        "CatalogItem", foreign_keys=[image3_id], back_populates="sections_image3"
    )
    image4 = relationship(
        "CatalogItem", foreign_keys=[image4_id], back_populates="sections_image4"
    )
    image5 = relationship(
        "CatalogItem", foreign_keys=[image5_id], back_populates="sections_image5"
    )
    image6 = relationship(
        "CatalogItem", foreign_keys=[image6_id], back_populates="sections_image6"
    )
    fav_image = relationship(
        "CatalogItem", foreign_keys=[fav_image_id], back_populates="sections_fav"
    )
    mr_questions = relationship(
        "MRQuestion", back_populates="section", cascade="all, delete-orphan"
    )
    mr_question_items = relationship(
        "MRQuestionItem", back_populates="section", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sections(id={self.id}, memory_reconstruction_id={self.memory_reconstruction_id}, order={self.display_order})>"
