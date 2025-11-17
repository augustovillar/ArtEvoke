from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum
from api_types.common import ImageItem


class ObjectiveQuestionType(str, Enum):
    """Types of objective questions available in evaluations"""
    period = "period"
    environment = "environment"
    emotion = "emotion"

class SaveSelectImageQuestionDTO(BaseModel):
    eval_id: str
    section_id: str
    image_selected_id: str
    image_distractor_0_id: str
    image_distractor_1_id: str
    elapsed_time: str

class SaveObjectiveQuestionDTO(BaseModel):
    eval_id: str
    question_type: ObjectiveQuestionType
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
    shown_images: List[ImageItem]
    distractors: List[ImageItem]

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


# ============================================================================
# Results DTOs - For displaying evaluation results
# ============================================================================

class ImageQuestionResult(BaseModel):
    section_number: int
    section_text: str
    shown_images: List[ImageItem]
    user_selected_image_id: str  
    user_selected_image: ImageItem  
    correct_image_id: str
    correct_image: ImageItem
    distractor_images: List[ImageItem]
    is_correct: bool
    time_spent: str  # Format: "HH:MM:SS"


class ObjectiveQuestionResult(BaseModel):
    question_type: ObjectiveQuestionType
    question_text: str
    options: List[str]
    user_answer: str  
    correct_answer: str
    is_correct: bool
    time_spent: str  # Format: "HH:MM:SS"


class MemoryReconstructionResultsDTO(BaseModel):
    story: str
    dataset: str
    language: str
    image_questions: List[ImageQuestionResult]
    objective_questions: List[ObjectiveQuestionResult]
    
    # Statistics
    total_image_questions: int
    correct_image_answers: int
    total_objective_questions: int
    correct_objective_answers: int
    image_accuracy: float  # Percentage
    objective_accuracy: float  # Percentage
    overall_accuracy: float  # Percentage


class StoryQuestionResult(BaseModel):
    user_answer: str
    time_spent: str  # Format: "HH:MM:SS"


class ChronologicalOrderResult(BaseModel):
    images: List[ImageItem]
    user_events: List[str]
    correct_events: List[str]
    is_correct_per_position: List[bool]
    is_fully_correct: bool
    correct_positions_count: int
    time_spent: str  # Format: "HH:MM:SS"


class ArtExplorationResultsDTO(BaseModel):
    story: str
    dataset: str
    language: str
    story_question: StoryQuestionResult
    chronological_order_question: ChronologicalOrderResult
    objective_questions: List[ObjectiveQuestionResult]
    
    # Statistics
    total_objective_questions: int
    correct_objective_answers: int
    objective_accuracy: float  # Percentage
    chronological_positions_correct: int
    chronological_total_positions: int
    chronological_accuracy: float  # Percentage
    overall_accuracy: float  # Percentage


class SessionResultsResponse(BaseModel):
    session_id: str
    mode: Literal["memory_reconstruction", "art_exploration"]
    status: str
    completed_at: Optional[datetime] = None
    
    # Module-specific results (only one will be populated)
    memory_reconstruction_results: Optional[MemoryReconstructionResultsDTO] = None
    art_exploration_results: Optional[ArtExplorationResultsDTO] = None

    class Config:
        from_attributes = True
