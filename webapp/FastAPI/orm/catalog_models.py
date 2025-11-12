"""
ORM models for art catalog tables: SemArt, Ipiranga, WikiArt, and CatalogItem.
"""

from sqlalchemy import Column, String, Text, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from .base import Base
from api_types.common import Dataset


class SemArt(Base):
    """SemArt table - stores artworks from the SemArt dataset."""

    __tablename__ = "SemArt"
    __table_args__ = (
        Index("idx_semart_artist_name", "artist_name"),
        Index("idx_semart_type", "type"),
        Index("idx_semart_art_school", "art_school"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    image_file = Column(String(36), nullable=True)
    description = Column(Text, nullable=True)
    artist_name = Column(String(100), nullable=True)
    title = Column(String(100), nullable=True)
    technique = Column(String(50), nullable=True)
    date = Column(String(50), nullable=True)
    type = Column(String(50), nullable=True)
    art_school = Column(String(50), nullable=True)
    description_generated = Column(Text, nullable=True)

    # Relationships
    catalog_items = relationship("CatalogItem", back_populates="semart")

    def __repr__(self):
        return f"<SemArt(id={self.id}, title={self.title}, artist={self.artist_name})>"


class Ipiranga(Base):
    """Ipiranga table - stores artworks from the Ipiranga museum."""

    __tablename__ = "Ipiranga"
    __table_args__ = (
        Index("idx_ipiranga_type", "type"),
        Index("idx_ipiranga_inventory_code", "inventory_code"),
        Index("idx_ipiranga_title", "title"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    external_id = Column(String(36), nullable=True)
    image_file = Column(String(100), nullable=True)
    inventory_code = Column(String(20), nullable=True)
    title = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=True)
    artist_name = Column(String(50), nullable=True)
    location = Column(String(50), nullable=True)
    date = Column(String(50), nullable=True)
    period = Column(String(20), nullable=True)
    technique = Column(String(50), nullable=True)
    height = Column(String(8), nullable=True)
    width = Column(String(8), nullable=True)
    color = Column(String(20), nullable=True)
    history = Column(Text, nullable=True)
    collection_alt_name = Column(Text, nullable=True)
    description_generated = Column(Text, nullable=True)

    # Relationships
    catalog_items = relationship("CatalogItem", back_populates="ipiranga")

    def __repr__(self):
        return f"<Ipiranga(id={self.id}, title={self.title}, inventory_code={self.inventory_code})>"


class WikiArt(Base):
    """WikiArt table - stores artworks from the WikiArt dataset."""

    __tablename__ = "WikiArt"
    __table_args__ = (
        Index("idx_wikiart_artist_name", "artist_name"),
        Index("idx_wikiart_type", "type"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    image_file = Column(String(50), nullable=True)
    artist_name = Column(String(50), nullable=True)
    type = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    width = Column(String(8), nullable=True)
    height = Column(String(8), nullable=True)
    description_generated = Column(Text, nullable=True)

    # Relationships
    catalog_items = relationship("CatalogItem", back_populates="wikiart")

    def __repr__(self):
        return f"<WikiArt(id={self.id}, artist={self.artist_name})>"


class CatalogItem(Base):
    """CatalogItem table - unified catalog linking to specific dataset items."""

    __tablename__ = "CatalogItem"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    ipiranga_id = Column(
        String(36),
        ForeignKey("Ipiranga.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    wikiart_id = Column(
        String(36),
        ForeignKey("WikiArt.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    semart_id = Column(
        String(36),
        ForeignKey("SemArt.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=True,
    )
    source = Column(
        Enum(Dataset, name="catalog_source"), nullable=False
    )

    # Relationships
    ipiranga = relationship("Ipiranga", back_populates="catalog_items")
    wikiart = relationship("WikiArt", back_populates="catalog_items")
    semart = relationship("SemArt", back_populates="catalog_items")

    images = relationship("Images", back_populates="catalog_item")
    sections_image1 = relationship(
        "Sections", foreign_keys="Sections.image1_id", back_populates="image1"
    )
    sections_image2 = relationship(
        "Sections", foreign_keys="Sections.image2_id", back_populates="image2"
    )
    sections_image3 = relationship(
        "Sections", foreign_keys="Sections.image3_id", back_populates="image3"
    )
    sections_image4 = relationship(
        "Sections", foreign_keys="Sections.image4_id", back_populates="image4"
    )
    sections_image5 = relationship(
        "Sections", foreign_keys="Sections.image5_id", back_populates="image5"
    )
    sections_image6 = relationship(
        "Sections", foreign_keys="Sections.image6_id", back_populates="image6"
    )
    sections_fav = relationship(
        "Sections", foreign_keys="Sections.fav_image_id", back_populates="fav_image"
    )
    mr_question_items = relationship("MRQuestionItem", back_populates="catalog_item")

    # SelectImageQuestion relationships
    select_image_questions_selected = relationship(
        "SelectImageQuestion",
        foreign_keys="SelectImageQuestion.image_selected_id",
        back_populates="image_selected",
    )
    select_image_questions_distractor_0 = relationship(
        "SelectImageQuestion",
        foreign_keys="SelectImageQuestion.image_distractor_0_id",
        back_populates="image_distractor_0",
    )
    select_image_questions_distractor_1 = relationship(
        "SelectImageQuestion",
        foreign_keys="SelectImageQuestion.image_distractor_1_id",
        back_populates="image_distractor_1",
    )

    def __repr__(self):
        return f"<CatalogItem(id={self.id}, source={self.source})>"
