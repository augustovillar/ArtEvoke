from pydantic import BaseModel, field_validator, model_validator
from typing import Optional, Literal
from datetime import date, datetime


# Session types
class SessionCreate(BaseModel):
    patient_id: str
    mode: Literal["art_exploration", "memory_reconstruction"]  # Only these two modes allowed
    interruption_time: Optional[int] = 10
    


class SessionUpdate(BaseModel):
    status: Optional[Literal["pending", "in_progress", "completed"]] = None
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
    status: Literal["pending", "in_progress", "completed"]
    memory_reconstruction_id: Optional[str] = None
    art_exploration_id: Optional[str] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
