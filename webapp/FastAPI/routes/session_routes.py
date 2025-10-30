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
from utils.auth import get_current_user
from api_types.session import SessionCreate, SessionUpdate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Create a new session for a patient (doctor only)"""
    # Verify doctor exists
    doctor = db.query(Doctor).filter(Doctor.id == current_user["id"]).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create sessions",
        )

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
            PatientDoctor.doctor_id == doctor.id,
            PatientDoctor.patient_id == session_data.patient_id
        )
        .first()
    )
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this patient",
        )

    # Create new session
    new_session = SessionModel(
        id=str(uuid.uuid4()),
        patient_id=session_data.patient_id,
        doctor_id=doctor.id,
        mode=session_data.mode,
        interruption_time=session_data.interruption_time or 10,
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
