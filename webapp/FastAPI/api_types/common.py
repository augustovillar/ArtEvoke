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

class SegmentationStrategy(str, Enum):
    conservative = "conservative"
    broader = "broader"


class ImageItem(BaseModel):
    image_url: str
    art_name: str
    id: str  # catalog_item_id
    source: str  # dataset source
    title: Optional[str] = None
    artist: Optional[str] = None
    year: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    description: Optional[str] = None
    technique: Optional[str] = None
    type: Optional[str] = None
    # SemArt specific
    art_school: Optional[str] = None
    # Ipiranga specific
    inventory_code: Optional[str] = None
    location: Optional[str] = None
    period: Optional[str] = None
    color: Optional[str] = None
    history: Optional[str] = None


class SearchImagesResponse(BaseModel):
    images: List[ImageItem]


class SectionItem(BaseModel):
    section: str
    images: List[ImageItem]


class SelectImagesResponse(BaseModel):
    sections: List[SectionItem]


class GenerateStoryResponse(BaseModel):
    text: str
    events: List[str]
    distractor: str
    environment: str
    timeOfDay: str
    emotion: str


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
    selectedImageIds: List[str]
    language: Language


class SelectImagesRVRequestDTO(BaseModel):
    story: str
    section_number: int

class SectionVRResponseDTO(SectionItem):
    sectionsQuantity: int

class ImproveTextRequestDTO(BaseModel):
    raw_text: str
    language: Optional[Language] = None

class ImproveTextResponseDTO(BaseModel):
    processed_text: str