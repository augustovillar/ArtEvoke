"""
Routes for evaluation functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from orm import get_db
from orm.evaluation_models import (
    Evaluation,
    SelectImageQuestion,
    ObjectiveQuestion,
    StoryOpenQuestion,
    ChronologicalOrderQuestion,
)
from orm.session_models import Session as SessionModel
from orm.memory_reconstruction_models import Sections, MemoryReconstruction
from orm.art_exploration_models import ArtExploration
from orm.catalog_models import CatalogItem
from api_types.evaluation import (
    SaveSelectImageQuestionDTO,
    SaveSelectImageQuestionResponseDTO,
    SaveObjectiveQuestionDTO,
    SaveObjectiveQuestionResponseDTO,
    SaveStoryOpenQuestionRequestDTO,
    SaveStoryOpenQuestionResponseDTO,
    GetChronologyEventsResponseDTO,
    SaveChronologicalOrderQuestionRequestDTO,
    SaveChronologicalOrderQuestionResponseDTO,
    GetSelectImageQuestionResponseDTO,
    GetProgressResponseDTO,
    CreateEvaluationResponseDTO,
    ImageInfoDTO,
)
from utils.auth import get_current_user, verify_evaluation_access, verify_session_access
from utils.embeddings import format_catalog_item_info
from datetime import datetime, time
import uuid

router = APIRouter()


def parse_time(time_str: str) -> time:
    """Parse time string in format HH:MM:SS to time object."""
    try:
        hours, minutes, seconds = map(int, time_str.split(":"))
        return time(hour=hours, minute=minutes, second=seconds)
    except (ValueError, AttributeError):
        return None


# ============================================================================
# COMMON EVALUATION ROUTES (both modes)
# ============================================================================

@router.post("/create", response_model=CreateEvaluationResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create evaluation for a session (works for both art exploration and memory reconstruction).
    Returns existing evaluation if already created.
    """
    session = verify_session_access(session_id, current_user, db)
    
    if session.art_exploration_id:
        mode = "art_exploration"
    elif session.memory_reconstruction_id:
        mode = "memory_reconstruction"
    else:
        raise HTTPException(
            status_code=400,
            detail="Session must have either art_exploration or memory_reconstruction linked"
        )
    
    existing_eval = db.query(Evaluation).filter(
        Evaluation.session_id == session_id
    ).first()
    
    if existing_eval:
        return CreateEvaluationResponseDTO(id=existing_eval.id)
    
    number_steps = 0
    if mode == "art_exploration":
        number_steps = 5
    elif mode == "memory_reconstruction":
        # Memory Reconstruction: N sections + 3 objective questions
        memory_reconstruction = db.query(MemoryReconstruction).filter(
            MemoryReconstruction.id == session.memory_reconstruction_id
        ).first()
        if memory_reconstruction:
            sections_count = db.query(Sections).filter(
                Sections.memory_reconstruction_id == memory_reconstruction.id
            ).count()
            number_steps = sections_count + 3
    
    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        mode=mode,
        number_steps=number_steps,
    )
    
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return CreateEvaluationResponseDTO(id=evaluation.id)


@router.post("/objective-question", response_model=SaveObjectiveQuestionResponseDTO, status_code=status.HTTP_201_CREATED)
async def save_objective_question(
    request: SaveObjectiveQuestionDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save an objective question answer (used by both art exploration and memory reconstruction).
    """
    evaluation, session = verify_evaluation_access(request.eval_id, current_user, db)
    
    # Create new answer
    question = ObjectiveQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        type=request.question_type,
        elapsed_time=parse_time(request.elapsed_time) if request.elapsed_time else None,
        selected_option=request.selected_option,
        correct_option=request.correct_option,
    )
    
    # Set options (up to 5)
    options_data = request.options[:5]  # Limit to 5 options
    for i, option in enumerate(options_data):
        setattr(question, f"option_{i}", option)
    
    db.add(question)
    
    evaluation.current_step += 1
    
    db.commit()
    db.refresh(question)
    
    return SaveObjectiveQuestionResponseDTO(id=question.id)


@router.get("/progress/{session_id}", response_model=GetProgressResponseDTO, status_code=status.HTTP_200_OK)
async def get_evaluation_progress(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get the current progress of evaluation (works for both art exploration and memory reconstruction).
    Returns current step, total steps, and completion status.
    """
    session = verify_session_access(session_id, current_user, db)
    
    # Get evaluation
    evaluation = db.query(Evaluation).filter(
        Evaluation.session_id == session_id
    ).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    return GetProgressResponseDTO(
        evaluation_started=True,
        eval_id=evaluation.id,
        current_step=evaluation.current_step,
        number_steps=evaluation.number_steps,
        is_completed=session.status == "completed",
    )


# ============================================================================
# ART EXPLORATION SPECIFIC ROUTES
# ============================================================================

@router.post("/art-exploration/story-open-question", response_model=SaveStoryOpenQuestionResponseDTO, status_code=status.HTTP_201_CREATED)
async def save_art_exploration_story_open_question(
    request: SaveStoryOpenQuestionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save story open question answer for art exploration."""
    evaluation, _ = verify_evaluation_access(request.eval_id, current_user, db)
    
    question = StoryOpenQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        text=request.text,
        elapsed_time=parse_time(request.elapsed_time) if request.elapsed_time else None,
    )
    
    db.add(question)
    
    evaluation.current_step += 1
    
    db.commit()
    db.refresh(question)
    
    return SaveStoryOpenQuestionResponseDTO(
        question_id=question.id
    )


@router.get("/art-exploration/chronology-events/{eval_id}", response_model=GetChronologyEventsResponseDTO, status_code=status.HTTP_200_OK)
async def get_art_exploration_chronology_events(
    eval_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get chronology events for art exploration evaluation."""
    _, session = verify_evaluation_access(eval_id, current_user, db)
    
    if not session.art_exploration_id:
        raise HTTPException(
            status_code=400,
            detail="Session does not have an art exploration associated"
        )
    
    art_exploration = db.query(ArtExploration).filter(
        ArtExploration.id == session.art_exploration_id
    ).first()
    
    if not art_exploration:
        raise HTTPException(status_code=404, detail="Art exploration not found")
    
    events = []
    if art_exploration.correct_option_0:
        events.append(art_exploration.correct_option_0)
    if art_exploration.correct_option_1:
        events.append(art_exploration.correct_option_1)
    if art_exploration.correct_option_2:
        events.append(art_exploration.correct_option_2)
    if art_exploration.correct_option_3:
        events.append(art_exploration.correct_option_3)
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail="No chronology events found for this art exploration"
        )
    
    return GetChronologyEventsResponseDTO(events=events)


@router.post("/art-exploration/chronological-order-question", response_model=SaveChronologicalOrderQuestionResponseDTO, status_code=status.HTTP_201_CREATED)
async def save_art_exploration_chronological_order_question(
    request: SaveChronologicalOrderQuestionRequestDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save chronological order question answer for art exploration."""
    evaluation, _ = verify_evaluation_access(request.eval_id, current_user, db)
    
    question = ChronologicalOrderQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        selected_option_0=request.selected_option_0,
        selected_option_1=request.selected_option_1,
        selected_option_2=request.selected_option_2,
        selected_option_3=request.selected_option_3,
        elapsed_time=parse_time(request.elapsed_time) if request.elapsed_time else None,
    )
    
    db.add(question)
    
    evaluation.current_step += 1
    
    db.commit()
    db.refresh(question)
    
    return SaveChronologicalOrderQuestionResponseDTO(
        question_id=question.id
    )


# ============================================================================
# MEMORY RECONSTRUCTION SPECIFIC ROUTES
# ============================================================================


@router.post("/memory-reconstruction/select-image-question", response_model=SaveSelectImageQuestionResponseDTO, status_code=status.HTTP_201_CREATED)
async def save_memory_reconstruction_select_image_question(
    request: SaveSelectImageQuestionDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a Memory Reconstruction select image question answer.
    """
    evaluation, _ = verify_evaluation_access(request.eval_id, current_user, db)
    
    question = SelectImageQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        section_id=request.section_id,
        image_selected_id=request.image_selected_id,
        image_distractor_0_id=request.image_distractor_0_id,
        image_distractor_1_id=request.image_distractor_1_id,
        elapsed_time=parse_time(request.elapsed_time) if request.elapsed_time else None,
    )
    
    db.add(question)
    
    # Increment current_step
    evaluation.current_step += 1
    
    db.commit()
    db.refresh(question)
    
    return SaveSelectImageQuestionResponseDTO(id=question.id)


@router.get("/memory-reconstruction/select-image-question/{session_id}/{section_id}", response_model=GetSelectImageQuestionResponseDTO, status_code=status.HTTP_200_OK)
async def get_select_image_question(
    session_id: str,
    section_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all 6 images from a specific section plus 2 random distractor images.
    Returns images from the same dataset.
    """
    session = verify_session_access(session_id, current_user, db)
    
    memory_reconstruction = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == session.memory_reconstruction_id
    ).first()
    
    if not memory_reconstruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Reconstruction not found"
        )
    
    # Get the specific section
    section = db.query(Sections).filter(
        Sections.id == section_id,
        Sections.memory_reconstruction_id == memory_reconstruction.id
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Get the 6 images from this specific section
    shown_image_ids = []
    for i in range(1, 7):  # image1 to image6
        image_id = getattr(section, f'image{i}_id', None)
        if image_id:
            shown_image_ids.append(image_id)
    
    shown_images = db.query(CatalogItem).options(
        joinedload(CatalogItem.wikiart),
        joinedload(CatalogItem.semart),
        joinedload(CatalogItem.ipiranga)
    ).filter(
        CatalogItem.id.in_(shown_image_ids)
    ).all()
    
    distractor_images = db.query(CatalogItem).options(
        joinedload(CatalogItem.wikiart),
        joinedload(CatalogItem.semart),
        joinedload(CatalogItem.ipiranga)
    ).filter(
        CatalogItem.source == memory_reconstruction.dataset,
        CatalogItem.id.notin_(shown_image_ids)
    ).order_by(func.rand()).limit(2).all()
    
    # Format images using the helper function
    shown_images_formatted = []
    for img in shown_images:
        formatted = format_catalog_item_info(img, include_full_metadata=False)
        if formatted:
            shown_images_formatted.append(ImageInfoDTO(**formatted))
    
    distractors = []
    for img in distractor_images:
        formatted = format_catalog_item_info(img, include_full_metadata=False)
        if formatted:
            distractors.append(ImageInfoDTO(**formatted))
    
    return GetSelectImageQuestionResponseDTO(
        shown_images=shown_images_formatted,
        distractors=distractors
    )


@router.post("/memory-reconstruction/complete/{session_id}", status_code=status.HTTP_200_OK)
async def complete_memory_reconstruction_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark Memory Reconstruction evaluation as complete and update session status.
    """
    session = verify_session_access(session_id, current_user, db)
    
   
    session.status = "completed"
    session.ended_at = datetime.utcnow().date()
    
    db.commit()

