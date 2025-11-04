"""
Routes for managing sessions between doctors and patients
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from routes import get_db
from orm import (
    Session as SessionModel,
    Patient,
    Doctor,
    PatientDoctor,
    MemoryReconstruction,
    ArtExploration,
)
from utils.auth import get_current_user, verify_doctor_role
from api_types.session import SessionCreate, SessionUpdate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Default interruption time (in seconds) - aligned with frontend config
DEFAULT_INTERRUPTION_TIME = 10


@router.get("/config/default-interruption-time")
async def get_default_interruption_time():
    """Get the default interruption time for sessions"""
    return {"default_interruption_time": DEFAULT_INTERRUPTION_TIME}


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new session for a patient (doctor only)"""
    # Validate mode (only 'memory_reconstruction' or 'art_exploration', NOT 'both')
    if session_data.mode not in ["memory_reconstruction", "art_exploration"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid mode. Must be 'memory_reconstruction' or 'art_exploration'",
        )
    
    # Validate interruption_time (use default if not provided, ensure within range)
    interruption_time = session_data.interruption_time if session_data.interruption_time is not None else DEFAULT_INTERRUPTION_TIME
    if interruption_time < 1 or interruption_time > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interruption time must be between 1 and 300 seconds",
        )
    
    # Verify user is doctor and get doctor ID
    doctor_id = verify_doctor_role(current_user)
    
    # Verify patient exists
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

    # Create evaluation instance based on session mode
    # DECISÃO: Criar o objeto do modo AGORA (na criação da sessão)
    # para ter o ID disponível imediatamente
    memory_reconstruction_id = None
    art_exploration_id = None

    # Create new session first to get session_id
    new_session = SessionModel(
        id=str(uuid.uuid4()),
        patient_id=session_data.patient_id,
        doctor_id=doctor_id,
        mode=session_data.mode,
        memory_reconstruction_id=None,  # Will be set after creating evaluation object
        art_exploration_id=None,  # Will be set after creating evaluation object
        interruption_time=interruption_time,
        status="pending",
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.flush()  # Get session ID without committing

    # Create evaluation instance based on session mode
    # Fields will be filled by patient during session (dataset, language, story, etc)
    if session_data.mode == "memory_reconstruction":
        mr_instance = MemoryReconstruction(
            id=str(uuid.uuid4()),
            patient_id=session_data.patient_id,
            session_id=new_session.id,
            story=None,  # Filled when patient starts session
            dataset=None,  # Selected during session by patient
            language=None,  # Selected during session by patient
            segmentation_strategy=None,  # Selected during session by patient
            created_at=datetime.utcnow(),
        )
        db.add(mr_instance)
        db.flush()
        new_session.memory_reconstruction_id = mr_instance.id

    elif session_data.mode == "art_exploration":
        ae_instance = ArtExploration(
            id=str(uuid.uuid4()),
            patient_id=session_data.patient_id,
            session_id=new_session.id,
            story_generated=None,  # Generated when patient completes session
            dataset=None,  # Selected during session by patient
            language=None,  # Selected during session by patient
            created_at=datetime.utcnow(),
        )
        db.add(ae_instance)
        db.flush()
        new_session.art_exploration_id = ae_instance.id

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
    # If it's a doctor, verify they have access to this patient
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
        .filter(SessionModel.status.in_(["pending", "in_progress"]))
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

    # Verify authorization
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

    # Update fields
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
    # Verify doctor
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

    # Verify doctor owns this session
    if session.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this session",
        )

    db.delete(session)
    db.commit()

    return None


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

    # Only patient can complete their sessions
    if current_user["id"] != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the patient can complete the session",
        )

    # Update session status
    session.status = "completed"
    session.ended_at = datetime.utcnow().date()

    db.commit()
    db.refresh(session)

    return session


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

    # Get MemoryReconstruction data if present
    if session.memory_reconstruction_id:
        mr = (
            db.query(MemoryReconstruction)
            .filter(MemoryReconstruction.id == session.memory_reconstruction_id)
            .first()
        )
        if mr:
            evaluation_data["memory_reconstruction"] = {
                "id": mr.id,
                "story": mr.story,
                "dataset": mr.dataset,
                "language": mr.language,
                "segmentation_strategy": mr.segmentation_strategy,
                "in_session": mr.in_session,
                "created_at": mr.created_at,
                "sections": [
                    {
                        "id": section.id,
                        "section_number": section.section_number,
                        "content": section.content,
                        "catalog_item_id": section.catalog_item_id,
                        "title": section.title,
                        "author": section.author,
                        "year": section.year,
                    }
                    for section in mr.sections
                ],
            }

    # Get ArtExploration data if present
    if session.art_exploration_id:
        ae = (
            db.query(ArtExploration)
            .filter(ArtExploration.id == session.art_exploration_id)
            .first()
        )
        if ae:
            evaluation_data["art_exploration"] = {
                "id": ae.id,
                "story_generated": ae.story_generated,
                "dataset": ae.dataset,
                "language": ae.language,
                "in_session": ae.in_session,
                "created_at": ae.created_at,
                "images": [
                    {
                        "id": image.id,
                        "image_number": image.image_number,
                        "catalog_item_id": image.catalog_item_id,
                        "title": image.title,
                        "author": image.author,
                        "year": image.year,
                    }
                    for image in ae.images
                ],
            }

    if not evaluation_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No evaluation data found for this session",
        )

    return evaluation_data
