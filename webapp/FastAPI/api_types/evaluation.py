from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


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


# ============================================================================
# Results DTOs - For displaying evaluation results
# ============================================================================

class ImageInfo(BaseModel):
    """Information about an image in the catalog"""
    id: str
    url: str
    name: str
    artist: Optional[str] = None
    title: Optional[str] = None


class ImageQuestionResult(BaseModel):
    """Results for an image selection question in Memory Reconstruction"""
    section_number: int
    section_text: str
    
    # Images shown to the user (6 original + 2 distractors)
    shown_images: List[ImageInfo]
    
    # User's answer
    user_selected_image_id: Optional[str] = None
    user_selected_image: Optional[ImageInfo] = None
    
    # Correct answer (the favorite from the section)
    correct_image_id: str
    correct_image: ImageInfo
    
    # Distractor images used
    distractor_images: List[ImageInfo]
    
    is_correct: bool
    time_spent: Optional[str] = None  # Format: "HH:MM:SS"


class ObjectiveQuestionResult(BaseModel):
    """Results for an objective question"""
    question_type: str  # environment, period, emotion
    question_text: str
    
    # Options available
    options: List[str]
    
    # User's answer
    user_answer: Optional[str] = None
    
    # Correct answer
    correct_answer: str
    
    is_correct: Optional[bool] = None
    time_spent: Optional[str] = None  # Format: "HH:MM:SS"


class MemoryReconstructionResultsDTO(BaseModel):
    """Complete results for Memory Reconstruction evaluation"""
    story: str
    dataset: str
    language: str
    
    # Questions results
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


class ArtExplorationResultsDTO(BaseModel):
    """Complete results for Art Exploration evaluation"""
    # TODO: Implement when Art Exploration results are needed
    story: str
    dataset: str
    language: str
    message: str = "Art Exploration results not yet implemented"


class SessionResultsResponse(BaseModel):
    """Response containing session results"""
    session_id: str
    mode: Literal["memory_reconstruction", "art_exploration"]
    status: str
    completed_at: Optional[datetime] = None
    
    # Module-specific results (only one will be populated)
    memory_reconstruction_results: Optional[MemoryReconstructionResultsDTO] = None
    art_exploration_results: Optional[ArtExplorationResultsDTO] = None

    class Config:
        from_attributes = True
