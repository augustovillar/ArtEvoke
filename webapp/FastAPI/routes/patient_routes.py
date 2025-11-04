from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, Patient
from api_types.patient import CompletePatientRequest, PatientLoginResponse, PatientInDB
from api_types.user import UserLogin, LoginResponse, MessageResponse
from utils.auth import verify_password, get_password_hash, create_access_token

router = APIRouter()


@router.post("/login")
async def patient_login(user_login: UserLogin, db: Session = Depends(get_db)) -> PatientLoginResponse:
    db_patient = db.query(Patient).filter(Patient.email == user_login.email).first()
    if not db_patient or not verify_password(user_login.password, db_patient.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"patientId": db_patient.id})
    patient_return = {
        "_id": db_patient.id,
        "email": db_patient.email,
        "name": db_patient.name,
    }

    return PatientLoginResponse(message="Login successful", token=access_token, user=patient_return)


@router.post("/complete")
async def complete_patient(request: CompletePatientRequest, db: Session = Depends(get_db)) -> MessageResponse:
    # Find patient by email and code
    patient = db.query(Patient).filter(
        Patient.email == request.email,
        Patient.code == request.code,
        Patient.status == 'pending'
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Invalid email or code")

    # Update patient with provided data
    from datetime import datetime
    patient.password = get_password_hash(request.password)
    patient.date_of_birth = datetime.strptime(request.date_of_birth, '%Y-%m-%d').date()
    patient.education_level = request.education_level
    patient.occupation = request.occupation
    patient.diseases = request.diseases
    patient.medications = request.medications
    patient.visual_impairment = request.visual_impairment
    patient.hearing_impairment = request.hearing_impairment
    patient.household_income = request.household_income
    patient.ethnicity = request.ethnicity
    patient.status = 'active'

    db.commit()

    return MessageResponse(message="Patient profile completed successfully")