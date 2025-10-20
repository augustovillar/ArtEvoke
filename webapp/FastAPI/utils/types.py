from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class Dataset(str, Enum):
    ipiranga = "ipiranga"
    wikiart = "wikiart"
    semart = "semart"


class Language(str, Enum):
    en = "en"
    pt = "pt"


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


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    username: str
    password: str


class SearchImagesRequestDTO(BaseModel):
    story: str
    language: Language
    dataset: Dataset


class SelectImagesPerSectionRequestDTO(BaseModel):
    story: str
    language: Language
    segmentation: str
    dataset: Dataset
    k: int


class GenerateStoryRequestDTO(BaseModel):
    selectedImagesByDataset: Dict[str, List[str]]


class SelectImagesRVRequestDTO(BaseModel):
    story: str
    dataset: Dataset
    sections: List[int]


class ImageItem(BaseModel):
    image_url: str
    art_name: str


class SearchImagesResponse(BaseModel):
    images: List[ImageItem]


class SectionItem(BaseModel):
    section: str
    images: List[ImageItem]


class SelectImagesResponse(BaseModel):
    sections: List[SectionItem]


class GenerateStoryResponse(BaseModel):
    text: str


class LoginResponse(BaseModel):
    message: str
    token: str
    user: UserInDB


class SaveStoryRequest(BaseModel):
    storyText: str
    selectedImagesByDataset: Dict[str, List[str]]


class SaveGenerationRequest(BaseModel):
    selectedImages: List[str]
    generatedStory: str


class MessageResponse(BaseModel):
    message: str


class RetrieveSearchesResponse(BaseModel):
    savedArtSearches: List[SavedArtSearch]
    savedStoryGenerations: List[SavedStoryGeneration]
