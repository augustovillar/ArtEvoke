"""
ORM models for user-related tables: Patient, Doctor, and PatientDoctor.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Date,
    DateTime,
    Boolean,
    DECIMAL,
    ForeignKey,
    Text,
    CheckConstraint,
    Enum,
)
from sqlalchemy.orm import relationship
from .base import Base


class Patient(Base):
    """Patient table - stores patient information."""

    __tablename__ = "Patient"
    __table_args__ = (
        CheckConstraint(
            "household_income IS NULL OR household_income >= 0",
            name="chk_patient_income",
        ),
        {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    id = Column(String(36), primary_key=True)
    username = Column(String(50), nullable=True, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    education_level = Column(String(50), nullable=True)
    occupation = Column(String(100), nullable=True)
    diseases = Column(Text, nullable=True)
    medications = Column(Text, nullable=True)
    visual_impairment = Column(Boolean, nullable=False, default=False)
    hearing_impairment = Column(Boolean, nullable=False, default=False)
    household_income = Column(DECIMAL(10, 2), nullable=True)
    ethnicity = Column(String(50), nullable=True)
    status = Column(Enum('pending', 'active'), nullable=False, default='pending')
    code = Column(String(4), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    doctors = relationship(
        "PatientDoctor", back_populates="patient", cascade="all, delete-orphan"
    )
    art_explorations = relationship("ArtExploration", back_populates="patient")
    memory_reconstructions = relationship(
        "MemoryReconstruction", back_populates="patient"
    )
    sessions = relationship("Session", back_populates="patient")

    def __repr__(self):
        return f"<Patient(id={self.id}, username={self.username}, name={self.name})>"


class Doctor(Base):
    """Doctor table - stores doctor/therapist information."""

    __tablename__ = "Doctor"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id = Column(String(36), primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    specialization = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    patients = relationship(
        "PatientDoctor", back_populates="doctor", cascade="all, delete-orphan"
    )
    sessions = relationship("Session", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, username={self.username}, name={self.name})>"


class PatientDoctor(Base):
    """PatientDoctor table - many-to-many relationship between patients and doctors."""

    __tablename__ = "PatientDoctor"
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    patient_id = Column(
        String(36),
        ForeignKey("Patient.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    doctor_id = Column(
        String(36),
        ForeignKey("Doctor.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    started_at = Column(Date, nullable=True)
    ended_at = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="doctors")
    doctor = relationship("Doctor", back_populates="patients")

    def __repr__(self):
        return (
            f"<PatientDoctor(patient_id={self.patient_id}, doctor_id={self.doctor_id})>"
        )
