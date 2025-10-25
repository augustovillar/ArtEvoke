from pydantic import BaseModel
from typing import Optional
from .user import MessageResponse


class CreatePatientRequest(BaseModel):
    name: str
    email: str
    doctor_id: str


class CreatePatientResponse(BaseModel):
    message: str
    code: str


class CompletePatientRequest(BaseModel):
    email: str
    code: str
    username: str
    password: str
    date_of_birth: str  # YYYY-MM-DD
    education_level: str
    occupation: str
    diseases: Optional[str] = None
    medications: Optional[str] = None
    visual_impairment: bool = False
    hearing_impairment: bool = False
    household_income: Optional[float] = None
    ethnicity: Optional[str] = None