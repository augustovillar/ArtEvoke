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
)
from orm.session_models import Session as SessionModel
from orm.memory_reconstruction_models import Sections, MemoryReconstruction
from orm.catalog_models import CatalogItem
from api_types.evaluation import (
    SaveSelectImageQuestionDTO,
    SaveObjectiveQuestionDTO,
)
from utils.auth import get_current_user
from datetime import datetime, timedelta
import uuid

router = APIRouter()


def milliseconds_to_time(milliseconds: float):
    """Convert milliseconds to time object."""
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    microseconds = int((seconds % 1) * 1_000_000)
    
    # Create a timedelta and convert to time
    td = timedelta(hours=hours, minutes=minutes, seconds=secs, microseconds=microseconds)
    base_time = datetime.min
    result_datetime = base_time + td
    return result_datetime.time()


@router.post("/memory-reconstruction/select-image-question")
async def save_memory_reconstruction_select_image_question(
    request: SaveSelectImageQuestionDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a Memory Reconstruction select image question answer.
    """
    # Verify evaluation exists and belongs to user's session
    evaluation = db.query(Evaluation).filter(Evaluation.id == request.eval_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id,
        SessionModel.patient_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this evaluation"
        )
    
    # Check if answer already exists for this section
    existing = db.query(SelectImageQuestion).filter(
        SelectImageQuestion.eval_id == request.eval_id,
        SelectImageQuestion.section_id == request.section_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Answer for this section already exists"
        )
    
    # Create new answer
    question = SelectImageQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        section_id=request.section_id,
        image_selected_id=request.image_selected_id,
        image_distractor_0_id=request.image_distractor_0_id,
        image_distractor_1_id=request.image_distractor_1_id,
        elapsed_time=milliseconds_to_time(request.elapsed_time),
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return {"message": "Answer saved successfully", "id": question.id}


@router.post("/memory-reconstruction/objective-question")
async def save_memory_reconstruction_objective_question(
    request: SaveObjectiveQuestionDTO,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Save a Memory Reconstruction objective question answer.
    """
    # Verify evaluation exists and belongs to user's session
    evaluation = db.query(Evaluation).filter(Evaluation.id == request.eval_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found"
        )
    
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id,
        SessionModel.patient_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this evaluation"
        )
    
    # Create new answer
    question = ObjectiveQuestion(
        id=str(uuid.uuid4()),
        eval_id=request.eval_id,
        type=request.question_type,
        elapsed_time=milliseconds_to_time(request.elapsed_time),
        selected_option=request.selected_option,
        correct_option=request.correct_option,
    )
    
    # Set options (up to 5)
    options_data = request.options[:5]  # Limit to 5 options
    for i, option in enumerate(options_data):
        setattr(question, f"option_{i}", option)
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return {"message": "Answer saved successfully", "id": question.id}


@router.post("/memory-reconstruction/start/{session_id}")
async def start_memory_reconstruction_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start Memory Reconstruction evaluation for a session.
    Creates the evaluation record when user enters evaluation phase.
    """
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.patient_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if evaluation already exists
    existing_evaluation = db.query(Evaluation).filter(
        Evaluation.session_id == session_id
    ).first()
    
    if existing_evaluation:
        return {
            "message": "Evaluation already exists",
            "eval_id": existing_evaluation.id
        }
    
    # Create new evaluation
    evaluation = Evaluation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        mode=session.mode,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    
    return {
        "message": "Evaluation started successfully",
        "eval_id": evaluation.id
    }


@router.get("/memory-reconstruction/distractor-images/{section_id}")
async def get_distractor_images(
    section_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get 2 random distractor images for a section.
    Returns images from the same dataset but different from the ones shown in the section.
    """
    # Get the section to know which images were shown
    section = db.query(Sections).filter(Sections.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Get the Memory Reconstruction to know the dataset
    memory_reconstruction = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == section.memory_reconstruction_id
    ).first()
    
    if not memory_reconstruction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Reconstruction not found"
        )
    
    # Collect IDs of images shown in this section
    shown_image_ids = []
    for i in range(1, 7):  # image1 to image6
        image_id = getattr(section, f'image{i}_id', None)
        if image_id:
            shown_image_ids.append(image_id)
    
    # Get 2 random images from the same dataset, excluding shown images
    # Use joinedload to eagerly load the related dataset tables
    distractor_images = db.query(CatalogItem).options(
        joinedload(CatalogItem.wikiart),
        joinedload(CatalogItem.semart),
        joinedload(CatalogItem.ipiranga)
    ).filter(
        CatalogItem.source == memory_reconstruction.dataset,
        CatalogItem.id.notin_(shown_image_ids)
    ).order_by(func.rand()).limit(2).all()
    
    if len(distractor_images) < 2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not enough images available for distractors"
        )
    
    # Build response with correct data based on source
    distractors = []
    for img in distractor_images:
        # Get title, artist and image URL based on source
        title = "Unknown"
        artist = "Unknown"
        image_url = None
        
        if img.source == "wikiart" and img.wikiart:
            # WikiArt doesn't have title field, use image_file or id as fallback
            title = img.wikiart.artist_name or img.id
            artist = img.wikiart.artist_name or "Unknown"
            image_url = f"/art-images/wikiart/{img.wikiart.image_file}" if img.wikiart.image_file else None
        elif img.source == "semart" and img.semart:
            title = img.semart.title or img.semart.image_file or "Unknown"
            artist = img.semart.artist_name or "Unknown"
            image_url = f"/art-images/semart/{img.semart.image_file}" if img.semart.image_file else None
        elif img.source == "ipiranga" and img.ipiranga:
            title = img.ipiranga.title or "Unknown"
            artist = img.ipiranga.artist_name or "Unknown"
            image_url = f"https://acervoonline.mp.usp.br/wp-content/uploads/tainacan-items{img.ipiranga.image_file}" if img.ipiranga.image_file else None
        
        # Skip images without valid URL
        if not image_url:
            continue
            
        distractors.append({
            "id": img.id,
            "url": image_url,
            "title": title,
            "artist": artist,
        })
    
    # Ensure we have at least 2 distractors
    if len(distractors) < 2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Not enough valid distractor images available"
        )
    
    return {"distractors": distractors}


@router.post("/memory-reconstruction/complete/{session_id}")
async def complete_memory_reconstruction_evaluation(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mark Memory Reconstruction evaluation as complete and update session status.
    """
    # Verify session belongs to user
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.patient_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update session status to completed
    session.status = "completed"
    session.ended_at = datetime.utcnow().date()
    
    db.commit()
    
    return {"message": "Evaluation completed successfully"}
