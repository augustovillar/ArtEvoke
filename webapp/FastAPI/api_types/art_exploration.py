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


class ArtExplorationResponse(BaseModel):
    id: str
    story_generated: Optional[str] = None
    dataset: Optional[Dataset] = None
    language: Optional[Language] = None
    created_at: datetime
    images: List[ImagesItem]


class RetrieveArtExplorationResponseDTO(BaseModel):
    art_explorations: List[ArtExplorationResponse]
    total_count: int
    has_more: bool