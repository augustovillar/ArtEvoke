from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


# Session types
class SessionCreate(BaseModel):
    patient_id: str
    mode: str  # "art_exploration" or "memory_reconstruction" (NOT "both")
    interruption_time: Optional[int] = 10
    
    class Config:
        # Add validation for mode
        json_schema_extra = {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "mode": "memory_reconstruction",
                "interruption_time": 10
            }
        }


class SessionUpdate(BaseModel):
    status: Optional[str] = None  # "pending", "in_progress", "completed"
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    memory_reconstruction_id: Optional[str] = None
    art_exploration_id: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    patient_id: str
    doctor_id: str
    mode: str
    interruption_time: int
    status: str
    memory_reconstruction_id: Optional[str] = None
    art_exploration_id: Optional[str] = None
    started_at: Optional[date] = None
    ended_at: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
