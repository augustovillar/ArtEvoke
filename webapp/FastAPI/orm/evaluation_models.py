"""
ORM models for Evaluation and related question tables.
"""

from datetime import datetime, time
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Time,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base


class Evaluation(Base):
    """Evaluation table - stores evaluation sessions."""

    __tablename__ = "Evaluation"
    __table_args__ = (
        Index("idx_eval_session", "session_id"),
        Index("idx_eval_mode", "mode"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    session_id = Column(
        String(36),
        ForeignKey("Session.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    mode = Column(
        Enum("art_exploration", "memory_reconstruction", name="evaluation_mode"),
        nullable=False,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="evaluations")
    select_image_questions = relationship(
        "SelectImageQuestion",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
    story_open_questions = relationship(
        "StoryOpenQuestion",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
    chronological_order_questions = relationship(
        "ChronologicalOrderQuestion",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )
    objective_questions = relationship(
        "ObjectiveQuestion",
        back_populates="evaluation",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Evaluation(id={self.id}, session_id={self.session_id}, mode={self.mode})>"


class SelectImageQuestion(Base):
    """SelectImageQuestion table - image selection questions."""

    __tablename__ = "SelectImageQuestion"
    __table_args__ = (
        Index("idx_siq_eval", "eval_id"),
        Index("idx_siq_section", "section_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    eval_id = Column(
        String(36),
        ForeignKey("Evaluation.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    elapsed_time = Column(Time, nullable=True)
    image_selected_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    section_id = Column(
        String(36),
        ForeignKey("Sections.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
    )
    image_distractor_0_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    image_distractor_1_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="select_image_questions")
    section = relationship("Sections", back_populates="select_image_questions")
    image_selected = relationship(
        "CatalogItem",
        foreign_keys=[image_selected_id],
        back_populates="select_image_questions_selected",
    )
    image_distractor_0 = relationship(
        "CatalogItem",
        foreign_keys=[image_distractor_0_id],
        back_populates="select_image_questions_distractor_0",
    )
    image_distractor_1 = relationship(
        "CatalogItem",
        foreign_keys=[image_distractor_1_id],
        back_populates="select_image_questions_distractor_1",
    )

    def __repr__(self):
        return f"<SelectImageQuestion(id={self.id}, eval_id={self.eval_id})>"


class StoryOpenQuestion(Base):
    """StoryOpenQuestion table - open-ended story questions."""

    __tablename__ = "StoryOpenQuestion"
    __table_args__ = (
        Index("idx_soq_eval", "eval_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    eval_id = Column(
        String(36),
        ForeignKey("Evaluation.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    elapsed_time = Column(Time, nullable=True)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="story_open_questions")

    def __repr__(self):
        return f"<StoryOpenQuestion(id={self.id}, eval_id={self.eval_id})>"


class ChronologicalOrderQuestion(Base):
    """ChronologicalOrderQuestion table - chronological ordering questions."""

    __tablename__ = "ChronologicalOrderQuestion"
    __table_args__ = (
        Index("idx_coq_eval", "eval_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    eval_id = Column(
        String(36),
        ForeignKey("Evaluation.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    elapsed_time = Column(Time, nullable=True)
    selected_option_0 = Column(String(100), nullable=True)
    selected_option_1 = Column(String(100), nullable=True)
    selected_option_2 = Column(String(100), nullable=True)
    selected_option_3 = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    evaluation = relationship(
        "Evaluation", back_populates="chronological_order_questions"
    )

    def __repr__(self):
        return f"<ChronologicalOrderQuestion(id={self.id}, eval_id={self.eval_id})>"


class ObjectiveQuestion(Base):
    """ObjectiveQuestion table - multiple choice and true/false questions."""

    __tablename__ = "ObjectiveQuestion"
    __table_args__ = (
        Index("idx_oq_eval", "eval_id"),
        Index("idx_oq_type", "type"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    eval_id = Column(
        String(36),
        ForeignKey("Evaluation.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    elapsed_time = Column(Time, nullable=True)
    type = Column(
        Enum("period","environment", "emotion", name="objective_question_type"),
        nullable=False,
    )
    option_0 = Column(String(100), nullable=True)
    option_1 = Column(String(100), nullable=True)
    option_2 = Column(String(100), nullable=True)
    option_3 = Column(String(100), nullable=True)
    option_4 = Column(String(100), nullable=True)
    selected_option = Column(String(100), nullable=True)
    correct_option = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="objective_questions")

    def __repr__(self):
        return f"<ObjectiveQuestion(id={self.id}, eval_id={self.eval_id}, type={self.type})>"
