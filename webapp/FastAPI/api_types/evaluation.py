"""
API types for evaluation functionality.
"""

from pydantic import BaseModel, Field
from typing import List


class SaveSelectImageQuestionDTO(BaseModel):
    """DTO for saving a select image question answer."""
    eval_id: str
    section_id: str
    image_selected_id: str
    image_distractor_0_id: str
    image_distractor_1_id: str
    elapsed_time: float = Field(..., description="Elapsed time in milliseconds")


class SaveObjectiveQuestionDTO(BaseModel):
    """DTO for saving an objective question answer."""
    eval_id: str
    question_type: str = Field(..., description="Type: period, environment, or emotion")
    options: List[str] = Field(..., description="All options presented to user")
    selected_option: str
    correct_option: str
    elapsed_time: float = Field(..., description="Elapsed time in milliseconds")
