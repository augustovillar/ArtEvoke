"""
ORM models for Memory Reconstruction questions and answers.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    ForeignKey,
    Enum,
    Integer,
    Boolean,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base


class MRQuestion(Base):
    """MRQuestion table - questions for Memory Reconstruction sessions."""

    __tablename__ = "MRQuestion"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    memory_reconstruction_id = Column(
        String(36),
        ForeignKey("MemoryReconstruction.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    section_id = Column(
        String(36),
        ForeignKey("Sections.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    qtype = Column(
        Enum("free_text", "multi_select", name="mr_question_type"), nullable=False
    )
    prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    memory_reconstruction = relationship(
        "MemoryReconstruction", back_populates="mr_questions"
    )
    section = relationship("Sections", back_populates="mr_questions")
    items = relationship(
        "MRQuestionItem", back_populates="question", cascade="all, delete-orphan"
    )
    answers = relationship(
        "MRAnswer", back_populates="question", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MRQuestion(id={self.id}, qtype={self.qtype}, section_id={self.section_id})>"


class MRQuestionItem(Base):
    """MRQuestionItem table - items displayed in MR questions (true images and distractors)."""

    __tablename__ = "MRQuestionItem"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    question_id = Column(
        String(36),
        ForeignKey("MRQuestion.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    image_id = Column(
        String(36),
        ForeignKey("CatalogItem.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    section_id = Column(
        String(36),
        ForeignKey("Sections.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    is_distractor = Column(Boolean, nullable=False, default=False)

    # Relationships
    question = relationship("MRQuestion", back_populates="items")
    catalog_item = relationship("CatalogItem", back_populates="mr_question_items")
    section = relationship("Sections", back_populates="mr_question_items")
    selected_answers = relationship(
        "MRAnswerSelectedItem", back_populates="item", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MRQuestionItem(id={self.id}, question_id={self.question_id}, is_distractor={self.is_distractor})>"


class MRAnswer(Base):
    """MRAnswer table - user's answer to an MR question."""

    __tablename__ = "MRAnswer"
    __table_args__ = (
        Index("idx_mra_q", "question_id"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    question_id = Column(
        String(36),
        ForeignKey("MRQuestion.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user_text = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    question = relationship("MRQuestion", back_populates="answers")
    selected_items = relationship(
        "MRAnswerSelectedItem", back_populates="answer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<MRAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"


class MRAnswerSelectedItem(Base):
    """MRAnswerSelectedItem table - which images the user selected in MR Q2."""

    __tablename__ = "MRAnswerSelectedItem"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    answer_id = Column(
        String(36),
        ForeignKey("MRAnswer.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id = Column(
        String(36),
        ForeignKey("MRQuestionItem.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )

    # Relationships
    answer = relationship("MRAnswer", back_populates="selected_items")
    item = relationship("MRQuestionItem", back_populates="selected_answers")

    def __repr__(self):
        return f"<MRAnswerSelectedItem(answer_id={self.answer_id}, item_id={self.item_id})>"
