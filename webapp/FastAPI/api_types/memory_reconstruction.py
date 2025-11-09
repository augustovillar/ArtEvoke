from datetime import datetime
from .common import Dataset, Language, SegmentationStrategy
from pydantic import BaseModel
from typing import List, Optional


class SectionMemoryReconstruction(BaseModel):
    section_content: str
    image1_id: str
    image2_id: str
    image3_id: str
    image4_id: str
    image5_id: str
    image6_id: str
    fav_image_id: str


class SaveMemoryReconstructionRequestDTO(BaseModel):
    story: str
    dataset: str
    language: str
    segmentation_strategy: str
    sections: List[SectionMemoryReconstruction]


class SectionResponse(SectionMemoryReconstruction):
    id: str
    section_content: str
    display_order: int


class MemoryReconstructionResponse(BaseModel):
    id: str
    story: str
    dataset: Dataset
    language: Language
    segmentation_strategy: SegmentationStrategy
    created_at: datetime
    sections: List[SectionResponse]


class RetrieveMemoryReconstructionsResponseDTO(BaseModel):
    memory_reconstructions: List[MemoryReconstructionResponse]
    total_count: int
    has_more: bool

