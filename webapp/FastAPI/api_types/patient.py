from pydantic import BaseModel
from typing import Optional
from .user import MessageResponse


class PatientInDB(BaseModel):
    _id: str
    email: str
    name: str


class PatientLoginResponse(BaseModel):
    message: str
    token: str
    user: PatientInDB


class CreatePatientRequest(BaseModel):
    name: str
    email: str


class CreatePatientResponse(BaseModel):
    message: str
    code: str


class CompletePatientRequest(BaseModel):
    email: str
    code: str
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