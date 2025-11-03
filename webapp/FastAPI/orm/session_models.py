"""
ORM models for Session, PreEvaluation, and PosEvaluation tables.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    ForeignKey,
    Enum,
    SmallInteger,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from .base import Base


class Session(Base):
    """Session table - stores therapy sessions."""

    __tablename__ = "Session"
    __table_args__ = (
        Index("idx_session_patient", "patient_id"),
        Index("idx_session_doctor", "doctor_id"),
        Index("idx_session_mr", "memory_reconstruction_id"),
        Index("idx_session_ae", "art_exploration_id"),
        Index("idx_session_mode", "mode"),
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
    doctor_id = Column(
        String(36),
        ForeignKey("Doctor.id", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    memory_reconstruction_id = Column(
        String(36),
        ForeignKey("MemoryReconstruction.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    art_exploration_id = Column(
        String(36),
        ForeignKey("ArtExploration.id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )
    mode = Column(
        Enum("art_exploration", "memory_reconstruction", name="session_mode"),
        nullable=False,
    )
    interruption_time = Column(
        SmallInteger, 
        nullable=False, 
        default=10,
        # Aligns with CHECK constraint in SQL: interruption_time BETWEEN 1 AND 300
    )
    status = Column(
        Enum("pending", "in_progress", "completed", name="session_status"),
        nullable=False,
        default="pending",
    )
    started_at = Column(Date, nullable=True)
    ended_at = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    doctor = relationship("Doctor", back_populates="sessions")
    memory_reconstruction = relationship(
        "MemoryReconstruction", 
        back_populates="sessions",
        foreign_keys="[Session.memory_reconstruction_id]"
    )
    art_exploration = relationship(
        "ArtExploration", 
        back_populates="sessions",
        foreign_keys="[Session.art_exploration_id]"
    )
    pre_evaluation = relationship(
        "PreEvaluation",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    pos_evaluation = relationship(
        "PosEvaluation",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    ae_questions = relationship(
        "AEQuestion", back_populates="session", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Session(id={self.id}, patient_id={self.patient_id}, mode={self.mode})>"
        )


class PreEvaluation(Base):
    """PreEvaluation table - pre-session evaluation questionnaire."""

    __tablename__ = "PreEvaluation"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    session_id = Column(
        String(36),
        ForeignKey("Session.id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    meds_changes = Column(String(100), nullable=True)
    alone = Column(String(1), nullable=True)  # Boolean as TINYINT(1)
    any_recent_conditions = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="pre_evaluation")

    def __repr__(self):
        return f"<PreEvaluation(id={self.id}, session_id={self.session_id})>"


class PosEvaluation(Base):
    """PosEvaluation table - post-session evaluation questionnaire."""

    __tablename__ = "PosEvaluation"
    __table_args__ = (
        CheckConstraint("experience BETWEEN 0 AND 10", name="chk_experience"),
        CheckConstraint("difficulty BETWEEN 0 AND 10", name="chk_difficulty"),
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
        unique=True,
    )
    experience = Column(SmallInteger, nullable=True)
    difficulty = Column(SmallInteger, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="pos_evaluation")

    def __repr__(self):
        return f"<PosEvaluation(id={self.id}, session_id={self.session_id})>"
