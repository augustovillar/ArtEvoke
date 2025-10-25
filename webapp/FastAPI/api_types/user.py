from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class SavedArtSearch(BaseModel):
    text: str
    selectedImagesByDataset: Dict[str, List[str]] = Field(default_factory=dict)
    dateAdded: datetime
    _id: Optional[str] = None


class SavedStoryGeneration(BaseModel):
    text: str
    images: List[str]
    dateAdded: datetime
    _id: Optional[str] = None


class User(BaseModel):
    username: str
    email: str
    password: str


class UserInDB(User):
    _id: str
    savedArtSearches: Optional[List[SavedArtSearch]] = []
    savedStoryGenerations: Optional[List[SavedStoryGeneration]] = []


class Doctor(BaseModel):
    username: str
    email: str
    password: str
    name: str
    date_of_birth: str  # YYYY-MM-DD
    specialization: str


class DoctorInDB(Doctor):
    _id: str
    name: str
    specialization: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


class DoctorLogin(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: str
    user: UserInDB


class MessageResponse(BaseModel):
    message: str


class RetrieveSearchesResponse(BaseModel):
    savedArtSearches: List[SavedArtSearch]
    savedStoryGenerations: List[SavedStoryGeneration]