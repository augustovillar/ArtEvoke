"""
ORM models for Art Exploration questions and answers.
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


class AEQuestion(Base):
    """AEQuestion table - questions for Art Exploration sessions."""

    __tablename__ = "AEQuestion"
    __table_args__ = (
        Index("idx_aeq_parent", "art_exploration_id", "qtype"),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    art_exploration_id = Column(
        String(36),
        ForeignKey("ArtExploration.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = Column(
        String(36),
        ForeignKey("Session.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    qtype = Column(
        Enum("order_free_text", "order_cards", "binary", name="ae_question_type"),
        nullable=False,
    )
    prompt = Column(Text, nullable=False)
    correct_text = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    art_exploration = relationship("ArtExploration", back_populates="ae_questions")
    session = relationship("Session", back_populates="ae_questions")
    items = relationship(
        "AEQuestionItem", back_populates="question", cascade="all, delete-orphan"
    )
    answers = relationship(
        "AEAnswer", back_populates="question", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AEQuestion(id={self.id}, qtype={self.qtype})>"


class AEQuestionItem(Base):
    """AEQuestionItem table - items that compose a question (cards/actions or binary options)."""

    __tablename__ = "AEQuestionItem"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    question_id = Column(
        String(36),
        ForeignKey("AEQuestion.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    content_text = Column(Text, nullable=False)
    is_distractor = Column(Boolean, nullable=False, default=False)
    correct_position = Column(Integer, nullable=True)

    # Relationships
    question = relationship("AEQuestion", back_populates="items")
    selected_answers = relationship(
        "AEAnswerSelectedItem", back_populates="item", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AEQuestionItem(id={self.id}, question_id={self.question_id})>"


class AEAnswer(Base):
    """AEAnswer table - user's answer to an AE question."""

    __tablename__ = "AEAnswer"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    question_id = Column(
        String(36),
        ForeignKey("AEQuestion.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    user_text = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    question = relationship("AEQuestion", back_populates="answers")
    selected_items = relationship(
        "AEAnswerSelectedItem", back_populates="answer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AEAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"


class AEAnswerSelectedItem(Base):
    """AEAnswerSelectedItem table - tracks which items the user selected and their order."""

    __tablename__ = "AEAnswerSelectedItem"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    answer_id = Column(
        String(36),
        ForeignKey("AEAnswer.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    item_id = Column(
        String(36),
        ForeignKey("AEQuestionItem.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    user_position = Column(Integer, nullable=True)

    # Relationships
    answer = relationship("AEAnswer", back_populates="selected_items")
    item = relationship("AEQuestionItem", back_populates="selected_answers")

    def __repr__(self):
        return f"<AEAnswerSelectedItem(answer_id={self.answer_id}, item_id={self.item_id})>"
