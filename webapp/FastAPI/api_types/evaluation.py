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
