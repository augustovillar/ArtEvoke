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

from pydantic import BaseModel
from typing import Optional, List


class CreateEvaluationResponseDTO(BaseModel):
    id: str


class SaveStoryOpenQuestionRequestDTO(BaseModel):
    eval_id: str
    text: str
    elapsed_time: Optional[str] = None


class SaveStoryOpenQuestionResponseDTO(BaseModel):
    question_id: str


class GetChronologyEventsResponseDTO(BaseModel):
    events: List[str]


class SaveChronologicalOrderQuestionRequestDTO(BaseModel):
    eval_id: str
    selected_option_0: Optional[str] = None
    selected_option_1: Optional[str] = None
    selected_option_2: Optional[str] = None
    selected_option_3: Optional[str] = None
    elapsed_time: Optional[str] = None


class SaveChronologicalOrderQuestionResponseDTO(BaseModel):
    question_id: str
