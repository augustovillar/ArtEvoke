from datetime import datetime
from .common import Dataset, Language, SegmentationStrategy
from pydantic import BaseModel
from typing import List, Optional

class ImagesItem(BaseModel):
    display_order: int
    id: str

class SaveArtExplorationRequestDTO(BaseModel):
    story_generated: str
    dataset: str
    language: str
    images_selected: List[ImagesItem]
    correct_option_0: Optional[str] = None
    correct_option_1: Optional[str] = None
    correct_option_2: Optional[str] = None
    correct_option_3: Optional[str] = None


class ArtExplorationResponse(BaseModel):
    id: str
    story_generated: str
    dataset: Dataset
    language: Language
    created_at: datetime
    images: List[ImagesItem]


class RetrieveArtExplorationResponseDTO(BaseModel):
    art_explorations: List[ArtExplorationResponse]
    total_count: int
    has_more: bool