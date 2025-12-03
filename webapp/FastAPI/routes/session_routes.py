from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
from orm.evaluation_models import ChronologicalOrderQuestion
from routes import get_db
from orm import (
    Session as SessionModel,
    Patient,
    Doctor,
    PatientDoctor,
    MemoryReconstruction,
    Sections,
    ArtExploration,
    CatalogItem,
    Evaluation,
    SelectImageQuestion,
    ObjectiveQuestion,
    PreEvaluation,
    PosEvaluation,
)
from utils.auth import get_current_user, verify_doctor_role
from utils.embeddings import format_catalog_item_info
from api_types.session import (
    SessionCreate, 
    SessionUpdate, 
    SessionResponse,
    PreEvaluationCreate,
    PreEvaluationResponse,
    PosEvaluationCreate,
    PosEvaluationResponse,
)
from api_types.common import ImageItem
from api_types.evaluation import (
    SessionResultsResponse,
    MemoryReconstructionResultsDTO,
    ArtExplorationResultsDTO,
    ImageQuestionResult,
    ObjectiveQuestionResult,
    ObjectiveQuestionType,
    StoryQuestionResult,
    ChronologicalOrderResult,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])

DEFAULT_INTERRUPTION_TIME = 10


@router.get("/config/default-interruption-time")
async def get_default_interruption_time():
    return {"default_interruption_time": DEFAULT_INTERRUPTION_TIME}


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if session_data.mode not in ["memory_reconstruction", "art_exploration"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Must be 'memory_reconstruction' or 'art_exploration'",
        )
    
    interruption_time = session_data.interruption_time if session_data.interruption_time is not None else DEFAULT_INTERRUPTION_TIME
    if interruption_time < 1 or interruption_time > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interruption time must be between 1 and 300 seconds",
        )
    
    doctor_id = verify_doctor_role(current_user)
    
    patient = db.query(Patient).filter(Patient.id == session_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    # Verify doctor has access to this patient
    relationship = (
        db.query(PatientDoctor)
        .filter(
            PatientDoctor.doctor_id == doctor_id,
            PatientDoctor.patient_id == session_data.patient_id
        )
        .first()
    )
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this patient",
        )
    
    new_session = SessionModel(
        id=str(uuid.uuid4()),
        patient_id=session_data.patient_id,
        doctor_id=doctor_id,
        mode=session_data.mode,
        memory_reconstruction_id=None,
        art_exploration_id=None,
        interruption_time=interruption_time,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("/patient/{patient_id}", response_model=List[SessionResponse])
async def get_patient_sessions(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get all sessions for a specific patient"""
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )

    # Allow access if user is the patient themselves
    if current_user["role"] == "patient" and current_user["id"] == patient_id:
        pass  # Patient can view their own sessions
    
    elif current_user["role"] == "doctor":
        relationship = (
            db.query(PatientDoctor)
            .filter(
                PatientDoctor.doctor_id == current_user["id"],
                PatientDoctor.patient_id == patient_id
            )
            .first()
        )
        if not relationship:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this patient",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view these sessions",
        )

    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.patient_id == patient_id)
        .order_by(SessionModel.created_at.desc())
        .all()
    )

    return sessions


@router.get("/my-sessions", response_model=List[SessionResponse])
async def get_my_sessions(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Get all sessions for the current patient"""
    if current_user["role"] != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint",
        )

    sessions = (
        db.query(SessionModel)
        .filter(SessionModel.patient_id == current_user["id"])
        .filter(SessionModel.status.in_(["pending", "in_progress", "in_evaluation", "completed"]))
        .order_by(SessionModel.created_at.desc())
        .all()
    )

    return sessions


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get a specific session by ID"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session",
        )

    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Update session (typically to mark as started or completed)"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Only patient can start/complete their sessions
    if current_user["id"] != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can update session status",
        )

    if session_update.status:
        session.status = session_update.status

    if session_update.started_at:
        session.started_at = session_update.started_at

    if session_update.ended_at:
        session.ended_at = session_update.ended_at

    if session_update.memory_reconstruction_id:
        session.memory_reconstruction_id = session_update.memory_reconstruction_id

    if session_update.art_exploration_id:
        session.art_exploration_id = session_update.art_exploration_id

    db.commit()
    db.refresh(session)

    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Delete a session (doctor only)"""
    doctor = db.query(Doctor).filter(Doctor.id == current_user["id"]).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can delete sessions",
        )

    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if session.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session",
        )

    db.delete(session)
    db.commit()


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Mark session as completed (called when patient finishes evaluation)"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    if current_user["id"] != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can complete the session",
        )

    session.status = "completed"
    session.ended_at = datetime.utcnow().date()

    db.commit()
    db.refresh(session)

    return session


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get session status to determine appropriate redirection"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Verify authorization
    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session",
        )

    return {
        "session_id": session.id,
        "mode": session.mode,
        "status": session.status,
        "art_exploration_id": session.art_exploration_id,
        "memory_reconstruction_id": session.memory_reconstruction_id,
        "interruption_time": session.interruption_time
    }


@router.get("/{session_id}/evaluation")
async def get_session_evaluation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the evaluation data (MemoryReconstruction or ArtExploration) linked to a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    # Verify authorization
    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session evaluation",
        )

    evaluation_data = {}

    if session.memory_reconstruction_id:
        evaluation_data["memory_reconstruction"] = _get_memory_reconstruction_evaluation_data(
            session.memory_reconstruction_id, db
        )

    if session.art_exploration_id:
        evaluation_data["art_exploration"] = _get_art_exploration_evaluation_data(
            session.art_exploration_id, db
        )

    return evaluation_data


@router.get("/{session_id}/results", response_model=SessionResultsResponse)
async def get_session_results(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify authorization (patient or their doctor)
    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this session's results",
        )
    
    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is not completed yet. Current status: {session.status}"
        )
    
    evaluation = db.query(Evaluation).filter(Evaluation.session_id == session_id).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evaluation found for this session"
        )
    
    if session.mode == "memory_reconstruction":
        mr_results = _build_memory_reconstruction_results(session, evaluation, db)
        
        return SessionResultsResponse(
            session_id=session.id,
            mode=session.mode,
            status=session.status,
            completed_at=session.ended_at,
            memory_reconstruction_results=mr_results,
            art_exploration_results=None
        )
    
    elif session.mode == "art_exploration":
        ae_results = _build_art_exploration_results(session, evaluation, db)
        
        return SessionResultsResponse(
            session_id=session.id,
            mode=session.mode,
            status=session.status,
            completed_at=session.ended_at,
            memory_reconstruction_results=None,
            art_exploration_results=ae_results
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown session mode: {session.mode}"
        )


# ============================================================================
# PRE-EVALUATION ENDPOINTS
# ============================================================================

@router.post("/{session_id}/pre-evaluation", response_model=PreEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_pre_evaluation(
    session_id: str,
    pre_eval_data: PreEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create pre-evaluation questionnaire for a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if current_user["id"] != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can create pre-evaluation",
        )
    
    existing_pre_eval = db.query(PreEvaluation).filter(
        PreEvaluation.session_id == session_id
    ).first()
    
    if existing_pre_eval:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pre-evaluation already exists for this session"
        )
    
    new_pre_eval = PreEvaluation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        meds_changes=pre_eval_data.meds_changes,
        alone=pre_eval_data.alone,
        any_recent_conditions=pre_eval_data.any_recent_conditions,
    )
    
    db.add(new_pre_eval)
    db.commit()
    db.refresh(new_pre_eval)
    
    return new_pre_eval


@router.get("/{session_id}/pre-evaluation", response_model=PreEvaluationResponse)
async def get_pre_evaluation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get pre-evaluation questionnaire for a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this pre-evaluation",
        )
    
    pre_eval = db.query(PreEvaluation).filter(
        PreEvaluation.session_id == session_id
    ).first()
    
    if not pre_eval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pre-evaluation not found for this session"
        )
    
    return pre_eval


# ============================================================================
# POS-EVALUATION ENDPOINTS
# ============================================================================

@router.post("/{session_id}/pos-evaluation", response_model=PosEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_pos_evaluation(
    session_id: str,
    pos_eval_data: PosEvaluationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create pos-evaluation questionnaire for a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if current_user["id"] != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can create pos-evaluation",
        )
    
    existing_pos_eval = db.query(PosEvaluation).filter(
        PosEvaluation.session_id == session_id
    ).first()
    
    if existing_pos_eval:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pos-evaluation already exists for this session"
        )
    
    new_pos_eval = PosEvaluation(
        id=str(uuid.uuid4()),
        session_id=session_id,
        experience=pos_eval_data.experience,
        difficulty=pos_eval_data.difficulty,
        observations=pos_eval_data.observations
    )
    
    db.add(new_pos_eval)
    db.commit()
    db.refresh(new_pos_eval)
    
    return new_pos_eval


@router.get("/{session_id}/pos-evaluation", response_model=PosEvaluationResponse)
async def get_pos_evaluation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get pos-evaluation questionnaire for a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    if (
        current_user["id"] != session.patient_id
        and current_user["id"] != session.doctor_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this pos-evaluation",
        )
    
    # Get pos-evaluation
    pos_eval = db.query(PosEvaluation).filter(
        PosEvaluation.session_id == session_id
    ).first()
    
    if not pos_eval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pos-evaluation not found for this session"
        )
    
    return pos_eval


# ============================================================================
# Helper functions for results processing
# ============================================================================

def _get_memory_reconstruction_evaluation_data(
    memory_reconstruction_id: str,
    db: Session
) -> dict:
    """
    Get Memory Reconstruction evaluation data for display.
    Returns formatted dictionary with sections and images.
    """
    mr = (
        db.query(MemoryReconstruction)
        .filter(MemoryReconstruction.id == memory_reconstruction_id)
        .first()
    )
    
    if not mr:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memory Reconstruction with ID {memory_reconstruction_id} not found"
        )
    
    sections_list = db.query(Sections).filter(
        Sections.memory_reconstruction_id == mr.id
    ).order_by(Sections.display_order).all()
    
    sections_data = []
    for section in sections_list:
        # Get all section images
        section_image_ids = [
            section.image1_id,
            section.image2_id,
            section.image3_id,
            section.image4_id,
            section.image5_id,
            section.image6_id,
        ]
        
        images_data = []
        for image_id in section_image_ids:
            if not image_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Section {section.display_order} has missing image ID"
                )
            
            catalog_item = db.query(CatalogItem).filter(CatalogItem.id == image_id).first()
            if not catalog_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Image {image_id} not found in catalog for section {section.display_order}"
                )
            
            image_item = format_catalog_item_info(catalog_item, include_full_metadata=True)
            if not image_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to format image {image_id} for section {section.display_order}"
                )
            
            images_data.append(image_item)
        
        # Get favorite image
        if not section.fav_image_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Section {section.display_order} has no favorite image"
            )
        
        fav_catalog_item = db.query(CatalogItem).filter(CatalogItem.id == section.fav_image_id).first()
        if not fav_catalog_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Favorite image {section.fav_image_id} not found in catalog for section {section.display_order}"
            )
        
        fav_image_data = format_catalog_item_info(fav_catalog_item, include_full_metadata=True)
        if not fav_image_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to format favorite image {section.fav_image_id} for section {section.display_order}"
            )
        
        section_dict = {
            "id": section.id,
            "display_order": section.display_order,
            "section_content": section.section_content,
            "images": images_data,
            "fav_image": fav_image_data,
        }
        sections_data.append(section_dict)
    
    # Validate required fields
    if not mr.dataset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction dataset is missing"
        )
    
    if not mr.language:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction language is missing"
        )
    
    if not mr.segmentation_strategy:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction segmentation strategy is missing"
        )
    
    if not mr.created_at:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction creation time is missing"
        )
    
    return {
        "id": mr.id,
        "story": mr.story,
        "dataset": mr.dataset.value,
        "language": mr.language.value,
        "segmentation_strategy": mr.segmentation_strategy.value,
        "created_at": mr.created_at.isoformat(),
        "sections": sections_data,
    }


def _get_art_exploration_evaluation_data(
    art_exploration_id: str,
    db: Session
) -> dict:
    """
    Get Art Exploration evaluation data for display.
    Returns formatted dictionary with images.
    """
    ae = (
        db.query(ArtExploration)
        .filter(ArtExploration.id == art_exploration_id)
        .first()
    )
    
    if not ae:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Art Exploration with ID {art_exploration_id} not found"
        )
    
    images_data = []
    for image in sorted(ae.images, key=lambda x: x.display_order):
        image_item = format_catalog_item_info(image.catalog_item, include_full_metadata=True)
        if not image_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to format image for Art Exploration"
            )
        
        # Convert to dict and add extra fields
        image_dict = image_item.model_dump()
        image_dict["display_order"] = image.display_order
        images_data.append(image_dict)
    
    # Validate required fields
    if not ae.dataset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration dataset is missing"
        )
    
    if not ae.language:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration language is missing"
        )
        
    if not ae.created_at:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration creation time is missing"
        )
    
    return {
        "id": ae.id,
        "story_generated": ae.story_generated,
        "dataset": ae.dataset.value,
        "language": ae.language.value,
        "created_at": ae.created_at.isoformat(),
        "images": images_data,
    }


def _time_to_string(time_obj):
    """Convert time object to string format HH:MM:SS"""
    if not time_obj:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Elapsed time not recorded for question"
        )
    return str(time_obj)


def _process_memory_reconstruction_image_questions(
    evaluation_id: str,
    db: Session
) -> tuple[List[ImageQuestionResult], int]:
    """
    Process image selection questions for Memory Reconstruction.
    Returns tuple of (question_results, correct_count)
    """
    image_questions = db.query(SelectImageQuestion).filter(
        SelectImageQuestion.eval_id == evaluation_id
    ).all()
    
    image_results = []
    correct_count = 0
    
    for img_q in image_questions:
        section = db.query(Sections).filter(Sections.id == img_q.section_id).first()
        if not section:
            continue
        
        # Get all section images IDs and map them to their catalog items
        section_image_ids = [
            section.image1_id,
            section.image2_id,
            section.image3_id,
            section.image4_id,
            section.image5_id,
            section.image6_id,
        ]
        
        # Build section_images list and create a mapping for quick lookup
        section_images = []
        section_images_map = {}
        for img_id in section_image_ids:
            catalog_item = db.query(CatalogItem).filter(CatalogItem.id == img_id).first()
            if not catalog_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Section image not found in catalog: {img_id}"
                )
            
            image_item = format_catalog_item_info(catalog_item, include_full_metadata=True)
            if not image_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to format catalog item: {img_id}"
                )
            
            section_images.append(image_item)
            section_images_map[img_id] = image_item
        
        # Get distractor images
        distractor_images = []
        if img_q.image_distractor_0_id:
            catalog_item = db.query(CatalogItem).filter(CatalogItem.id == img_q.image_distractor_0_id).first()
            if not catalog_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Distractor image 0 not found in catalog: {img_q.image_distractor_0_id}"
                )
            
            image_item = format_catalog_item_info(catalog_item, include_full_metadata=True)
            if not image_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to format distractor image 0: {img_q.image_distractor_0_id}"
                )
            
            distractor_images.append(image_item)
        
        if img_q.image_distractor_1_id:
            catalog_item = db.query(CatalogItem).filter(CatalogItem.id == img_q.image_distractor_1_id).first()
            if not catalog_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Distractor image 1 not found in catalog: {img_q.image_distractor_1_id}"
                )
            
            image_item = format_catalog_item_info(catalog_item, include_full_metadata=True)
            if not image_item:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to format distractor image 1: {img_q.image_distractor_1_id}"
                )
            
            distractor_images.append(image_item)
        
        # Combine all shown images
        shown_images = section_images + distractor_images
        
        if not img_q.image_selected_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User did not select an image for section {section.display_order}"
            )
        
        # Get user selected image directly from database
        catalog_item = db.query(CatalogItem).filter(CatalogItem.id == img_q.image_selected_id).first()
        if not catalog_item:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User selected image not found in catalog: {img_q.image_selected_id}"
            )
        
        user_selected = format_catalog_item_info(catalog_item, include_full_metadata=True)
        if not user_selected:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to format user selected image: {img_q.image_selected_id}"
            )
        
        # Get correct image from section_images_map (already loaded)
        correct_image = section_images_map.get(section.fav_image_id)
        
        if not correct_image:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Correct image not found in section images: {section.fav_image_id}"
            )
        
        # Check if correct
        is_correct = (img_q.image_selected_id == section.fav_image_id)
        if is_correct:
            correct_count += 1
        
        image_results.append(ImageQuestionResult(
            section_number=section.display_order,
            section_text=section.section_content,
            shown_images=shown_images,
            user_selected_image_id=img_q.image_selected_id,
            user_selected_image=user_selected,
            correct_image_id=section.fav_image_id,
            correct_image=correct_image,
            distractor_images=distractor_images,
            is_correct=is_correct,
            time_spent=_time_to_string(img_q.elapsed_time)
        ))
    
    # Sort by section number
    image_results.sort(key=lambda x: x.section_number)
    
    return image_results, correct_count


def _process_objective_questions(
    evaluation: Evaluation,
    db: Session
) -> List[ObjectiveQuestionResult]:
    session = db.query(SessionModel).filter(
        SessionModel.id == evaluation.session_id
    ).first()
    
    if not session:
        return []
    
    language = "en"
    if session.memory_reconstruction_id:
        mr = db.query(MemoryReconstruction).filter(
            MemoryReconstruction.id == session.memory_reconstruction_id
        ).first()
        if mr:
            language = mr.language.value
    elif session.art_exploration_id:
        ae = db.query(ArtExploration).filter(
            ArtExploration.id == session.art_exploration_id
        ).first()
        if ae:
            language = ae.language.value
    
    question_type_map = {
        ObjectiveQuestionType.environment: {
            "pt": "Como era o ambiente da história?",
            "en": "What was the environment of the story?"
        },
        ObjectiveQuestionType.period: {
            "pt": "Que parte do dia era?",
            "en": "What time of day was it?"
        },
        ObjectiveQuestionType.emotion: {
            "pt": "Qual era a emoção predominante?",
            "en": "What was the predominant emotion?"
        }
    }
    
    objective_questions = db.query(ObjectiveQuestion).filter(
        ObjectiveQuestion.eval_id == evaluation.id
    ).order_by(ObjectiveQuestion.created_at).all()
    
    objective_results = []
    
    for obj_q in objective_questions:
        question_text = question_type_map.get(obj_q.type, {}).get(
            language,
            f"Question about {obj_q.type}"
        )
        
        options = []
        for i in range(5):
            option = getattr(obj_q, f"option_{i}", None)
            if option:
                options.append(option)

        if not obj_q.selected_option:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User did not answer objective question of type {obj_q.type}"
            )
        
        if not obj_q.correct_option:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Correct option missing for objective question of type {obj_q.type}"
            )
        
        is_correct = (obj_q.selected_option == obj_q.correct_option)
        
        objective_results.append(ObjectiveQuestionResult(
            question_type=obj_q.type,
            question_text=question_text,
            options=options,
            user_answer=obj_q.selected_option,
            correct_answer=obj_q.correct_option,
            is_correct=is_correct,
            time_spent=_time_to_string(obj_q.elapsed_time)
        ))
    
    return objective_results


def _process_memory_reconstruction_objective_questions(
    evaluation_id: str,
    language: str,
    db: Session
) -> tuple[List[ObjectiveQuestionResult], int]:

    question_type_map = {
        ObjectiveQuestionType.environment: {
            "pt": "Como era o ambiente da história?",
            "en": "What was the environment of the story?"
        },
        ObjectiveQuestionType.period: {
            "pt": "Que parte do dia era?",
            "en": "What time of day was it?"
        },
        ObjectiveQuestionType.emotion: {
            "pt": "Qual era a emoção predominante?",
            "en": "What was the predominant emotion?"
        }
    }
    
    objective_questions = db.query(ObjectiveQuestion).filter(
        ObjectiveQuestion.eval_id == evaluation_id
    ).order_by(ObjectiveQuestion.created_at).all()
    
    objective_results = []
    correct_count = 0
    
    for obj_q in objective_questions:
        question_text = question_type_map.get(obj_q.type, {}).get(
            language,
            f"Question about {obj_q.type}"
        )
        
        options = []
        for i in range(5):
            option = getattr(obj_q, f"option_{i}", None)
            if option:
                options.append(option)
        
        if not obj_q.selected_option:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User did not answer objective question of type {obj_q.type}"
            )
        
        if not obj_q.correct_option:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Correct option missing for objective question of type {obj_q.type}"
            )
        
        is_correct = (obj_q.selected_option == obj_q.correct_option)
        if is_correct:
            correct_count += 1
        
        objective_results.append(ObjectiveQuestionResult(
            question_type=obj_q.type,
            question_text=question_text,
            options=options,
            user_answer=obj_q.selected_option,
            correct_answer=obj_q.correct_option,
            is_correct=is_correct,
            time_spent=_time_to_string(obj_q.elapsed_time)
        ))
    
    return objective_results, correct_count


def _build_memory_reconstruction_results(
    session: SessionModel,
    evaluation: Evaluation,
    db: Session
) -> MemoryReconstructionResultsDTO:

    mr = db.query(MemoryReconstruction).filter(
        MemoryReconstruction.id == session.memory_reconstruction_id
    ).first()
    
    if not mr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory Reconstruction data not found"
        )
    
    image_results, correct_image_count = _process_memory_reconstruction_image_questions(
        evaluation.id, db
    )
    
    objective_results, correct_objective_count = _process_memory_reconstruction_objective_questions(
        evaluation.id,
        mr.language.value if mr.language else "pt",
        db
    )
    
    # Calculate statistics
    total_image = len(image_results)
    total_objective = len(objective_results)
    total_questions = total_image + total_objective
    
    image_accuracy = (correct_image_count / total_image * 100) if total_image > 0 else 0
    objective_accuracy = (correct_objective_count / total_objective * 100) if total_objective > 0 else 0
    overall_accuracy = ((correct_image_count + correct_objective_count) / total_questions * 100) if total_questions > 0 else 0
    
    # Validate required fields
    if not mr.dataset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction dataset is missing"
        )
    
    if not mr.language:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Memory Reconstruction language is missing"
        )
    
    return MemoryReconstructionResultsDTO(
        story=mr.story,
        dataset=mr.dataset.value,
        language=mr.language.value,
        image_questions=image_results,
        objective_questions=objective_results,
        total_image_questions=total_image,
        correct_image_answers=correct_image_count,
        total_objective_questions=total_objective,
        correct_objective_answers=correct_objective_count,
        image_accuracy=round(image_accuracy, 2),
        objective_accuracy=round(objective_accuracy, 2),
        overall_accuracy=round(overall_accuracy, 2)
    )


def _process_story_question(evaluation: Evaluation, db: Session) -> StoryQuestionResult:
    """Process story open question results"""
    from orm.evaluation_models import StoryOpenQuestion
    from api_types.evaluation import StoryQuestionResult
    
    story_q = db.query(StoryOpenQuestion).filter(
        StoryOpenQuestion.eval_id == evaluation.id
    ).first()
    
    if not story_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story question not found in evaluation"
        )
    
    return StoryQuestionResult(
        user_answer=story_q.text or "",
        time_spent=_time_to_string(story_q.elapsed_time)
    )


def _process_chronological_order_question(
    evaluation: Evaluation,
    art_exploration: ArtExploration,
    db: Session
) -> ChronologicalOrderResult:
    """Process chronological order question results"""
    
    chrono_q = db.query(ChronologicalOrderQuestion).filter(
        ChronologicalOrderQuestion.eval_id == evaluation.id
    ).first()
    
    if not chrono_q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chronological order question not found in evaluation"
        )
    
    # Get the correct order of events (strings)
    correct_events = []
    for i in range(4):
        event = getattr(art_exploration, f"correct_option_{i}")
        if event:
            correct_events.append(event)
    
    if len(correct_events) != 4:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Incomplete correct events data in art exploration"
        )

    user_events = []
    for i in range(4):
        event = getattr(chrono_q, f"selected_option_{i}")
        if event:
            user_events.append(event)
    
    if len(user_events) != 4:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Incomplete user events data in chronological order question"
        )
    
    is_correct_per_position = [
        user_events[i] == correct_events[i] for i in range(4)
    ]
    
    correct_positions_count = sum(is_correct_per_position)
    is_fully_correct = correct_positions_count == 4
    
    return ChronologicalOrderResult(
        user_events=user_events,
        correct_events=correct_events,
        is_correct_per_position=is_correct_per_position,
        is_fully_correct=is_fully_correct,
        correct_positions_count=correct_positions_count,
        time_spent=_time_to_string(chrono_q.elapsed_time)
    )


def _build_art_exploration_results(
    session: SessionModel,
    evaluation: Evaluation,
    db: Session
) -> ArtExplorationResultsDTO:
    """Build Art Exploration results DTO"""
    
    ae = db.query(ArtExploration).filter(
        ArtExploration.id == session.art_exploration_id
    ).first()
    
    if not ae:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Art Exploration data not found"
        )
    
    story_question = _process_story_question(evaluation, db)
    chronological_order_question = _process_chronological_order_question(evaluation, ae, db)
    objective_questions = _process_objective_questions(evaluation, db)
    
    total_objective = len(objective_questions)
    correct_objective = sum(1 for q in objective_questions if q.is_correct)
    objective_accuracy = (correct_objective / total_objective * 100) if total_objective > 0 else 0.0
    
    chronological_positions_correct = chronological_order_question.correct_positions_count
    chronological_total_positions = 4
    chronological_accuracy = (chronological_positions_correct / chronological_total_positions * 100)
    
    total_questions = total_objective + 1  # +1 for chronological order
    correct_answers = correct_objective + (1 if chronological_order_question.is_fully_correct else 0)
    overall_accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0.0
    
    if not ae.dataset:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration dataset is missing"
        )
    
    if not ae.language:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration language is missing"
        )
        
    if not ae.story_generated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Art Exploration story is missing"
        )
    
    return ArtExplorationResultsDTO(
        story=ae.story_generated,
        dataset=ae.dataset.value,
        language=ae.language.value,
        story_question=story_question,
        chronological_order_question=chronological_order_question,
        objective_questions=objective_questions,
        total_objective_questions=total_objective,
        correct_objective_answers=correct_objective,
        objective_accuracy=round(objective_accuracy, 2),
        chronological_positions_correct=chronological_positions_correct,
        chronological_total_positions=chronological_total_positions,
        chronological_accuracy=round(chronological_accuracy, 2),
        overall_accuracy=round(overall_accuracy, 2)
    )

