from pydantic import BaseModel
from typing import List

class ImageInfoDTO(BaseModel):
    id: str
    image_url: str
    art_name: str
    source: str

class SaveSelectImageQuestionDTO(BaseModel):
    eval_id: str
    section_id: str
    image_selected_id: str
    image_distractor_0_id: str
    image_distractor_1_id: str
    elapsed_time: str

class SaveObjectiveQuestionDTO(BaseModel):
    eval_id: str
    question_type: str
    options: List[str]
    selected_option: str
    correct_option: str
    elapsed_time: str 

class CreateEvaluationResponseDTO(BaseModel):
    id: str

class SaveStoryOpenQuestionRequestDTO(BaseModel):
    eval_id: str
    text: str
    elapsed_time: str

class SaveStoryOpenQuestionResponseDTO(BaseModel):
    question_id: str

class GetChronologyEventsResponseDTO(BaseModel):
    events: List[str]

class SaveChronologicalOrderQuestionRequestDTO(BaseModel):
    eval_id: str
    selected_option_0: str = None
    selected_option_1: str = None
    selected_option_2: str = None
    selected_option_3: str = None
    elapsed_time: str

class SaveChronologicalOrderQuestionResponseDTO(BaseModel):
    question_id: str

class GetSelectImageQuestionResponseDTO(BaseModel):
    shown_images: List[ImageInfoDTO]
    distractors: List[ImageInfoDTO]

class SaveSelectImageQuestionResponseDTO(BaseModel):
    id: str

class SaveObjectiveQuestionResponseDTO(BaseModel):
    id: str

class GetProgressResponseDTO(BaseModel):
    evaluation_started: bool
    eval_id: str
    current_step: int
    number_steps: int
    is_completed: bool
