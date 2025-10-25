"""
ORM package for ArtEvoke application.
Provides SQLAlchemy models for all database tables.
"""

# Base and database utilities
from .base import Base, init_db, get_db, create_all_tables, drop_all_tables

# User models
from .user_models import Patient, Doctor, PatientDoctor

# Catalog models
from .catalog_models import SemArt, Ipiranga, WikiArt, CatalogItem

# Art Exploration models
from .art_exploration_models import ArtExploration, Images

# Memory Reconstruction models
from .memory_reconstruction_models import MemoryReconstruction, Sections

# Session models
from .session_models import Session, PreEvaluation, PosEvaluation

# Art Exploration question models
from .ae_question_models import (
    AEQuestion,
    AEQuestionItem,
    AEAnswer,
    AEAnswerSelectedItem,
)

# Memory Reconstruction question models
from .mr_question_models import (
    MRQuestion,
    MRQuestionItem,
    MRAnswer,
    MRAnswerSelectedItem,
)

__all__ = [
    # Base
    "Base",
    "init_db",
    "get_db",
    "create_all_tables",
    "drop_all_tables",
    # Users
    "Patient",
    "Doctor",
    "PatientDoctor",
    # Catalog
    "SemArt",
    "Ipiranga",
    "WikiArt",
    "CatalogItem",
    # Art Exploration
    "ArtExploration",
    "Images",
    # Memory Reconstruction
    "MemoryReconstruction",
    "Sections",
    # Session
    "Session",
    "PreEvaluation",
    "PosEvaluation",
    # Art Exploration Questions
    "AEQuestion",
    "AEQuestionItem",
    "AEAnswer",
    "AEAnswerSelectedItem",
    # Memory Reconstruction Questions
    "MRQuestion",
    "MRQuestionItem",
    "MRAnswer",
    "MRAnswerSelectedItem",
]
