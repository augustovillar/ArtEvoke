from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import date, datetime


# Session types
class SessionCreate(BaseModel):
    patient_id: str
    mode: Literal["art_exploration", "memory_reconstruction"]  # Only these two modes allowed
    interruption_time: Optional[int] = 10
    


class SessionUpdate(BaseModel):
    status: Optional[Literal["pending", "in_progress", "in_evaluation", "completed"]] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    memory_reconstruction_id: Optional[str] = None
    art_exploration_id: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    mode: Literal["art_exploration", "memory_reconstruction"]
    interruption_time: int
    status: Literal["pending", "in_progress", "in_evaluation", "completed"]
    memory_reconstruction_id: Optional[str] = None
    art_exploration_id: Optional[str] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


# PreEvaluation types
class PreEvaluationCreate(BaseModel):
    meds_changes: Optional[str] = None
    alone: bool
    any_recent_conditions: Optional[str] = None


class PreEvaluationResponse(BaseModel):
    id: str
    session_id: str
    meds_changes: Optional[str] = None
    alone: bool
    any_recent_conditions: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# PosEvaluation types
class PosEvaluationCreate(BaseModel):
    experience: Optional[int] = None
    difficulty: Optional[int] = None
    observations: Optional[str] = None

    @field_validator('experience', 'difficulty')
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError('Rating must be between 0 and 10')
        return v


class PosEvaluationResponse(BaseModel):
    id: str
    session_id: str
    experience: Optional[int] = None
    difficulty: Optional[int] = None
    observations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
