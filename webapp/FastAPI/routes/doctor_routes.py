from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orm import get_db, Patient, Doctor as DoctorORM, PatientDoctor
from api_types.user import Doctor, DoctorInDB, DoctorLogin, LoginResponse, MessageResponse
from utils.auth import verify_password, get_password_hash, create_access_token, get_current_doctor
from api_types.patient import CreatePatientRequest, CreatePatientResponse
import uuid
import random
import string
from datetime import datetime

router = APIRouter()


@router.post("/signup")
async def doctor_signup(doctor: Doctor, db: Session = Depends(get_db)) -> DoctorInDB:
    print(f"Attempting doctor signup for email: {doctor.email}")
    # Check if email already exists
    existing_doctor_email = db.query(DoctorORM).filter(DoctorORM.email == doctor.email).first()
    if existing_doctor_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(doctor.password)

    # Create new doctor
    new_doctor = DoctorORM(
        id=str(uuid.uuid4()),
        email=doctor.email,
        password=hashed_password,
        name=doctor.name,
        date_of_birth=datetime.strptime(doctor.date_of_birth, '%Y-%m-%d').date(),
        specialization=doctor.specialization,
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return DoctorInDB(
        _id=new_doctor.id,
        email=new_doctor.email,
        password=new_doctor.password,
        name=new_doctor.name,
        date_of_birth=new_doctor.date_of_birth.strftime('%Y-%m-%d'),
        specialization=new_doctor.specialization,
    )


@router.post("/login")
async def doctor_login(doctor_login: DoctorLogin, db: Session = Depends(get_db)) -> LoginResponse:
    db_doctor = db.query(DoctorORM).filter(DoctorORM.email == doctor_login.email).first()
    if not db_doctor or not verify_password(doctor_login.password, db_doctor.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"doctorId": db_doctor.id})
    doctor_return = DoctorInDB(
        _id=db_doctor.id,
        email=db_doctor.email,
        password=db_doctor.password,
        name=db_doctor.name,
        date_of_birth=db_doctor.date_of_birth.strftime('%Y-%m-%d'),
        specialization=db_doctor.specialization,
    )

    return {"message": "Login successful", "token": access_token, "user": doctor_return}


@router.get("/profile")
async def get_doctor_profile(current_doctor: str = Depends(get_current_doctor), db: Session = Depends(get_db)) -> DoctorInDB:
    doctor = db.query(Doctor).filter(Doctor.id == current_doctor).first()
    return DoctorInDB(
        _id=doctor.id,
        email=doctor.email,
        password=doctor.password,
        name=doctor.name,
        specialization=doctor.specialization,
    )


@router.get("/patients")
async def get_doctor_patients(current_doctor: str = Depends(get_current_doctor), db: Session = Depends(get_db)):
    # Get all patients associated with this doctor using a join for better performance
    patients_query = db.query(Patient, PatientDoctor).join(
        PatientDoctor, Patient.id == PatientDoctor.patient_id
    ).filter(PatientDoctor.doctor_id == current_doctor).all()
    
    patients = []
    for patient, patient_doctor in patients_query:
        patients.append({
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "status": patient.status,
            "is_active": patient.status == 'active',
            "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
            "education_level": patient.education_level,
            "occupation": patient.occupation,
            "visual_impairment": patient.visual_impairment,
            "hearing_impairment": patient.hearing_impairment,
            "created_at": patient.created_at.isoformat(),
            "relationship_started": patient_doctor.started_at.isoformat() if patient_doctor.started_at else None,
            "relationship_ended": patient_doctor.ended_at.isoformat() if patient_doctor.ended_at else None,
        })
    
    # Return a plain list of patients (frontend expects an array)
    return patients


def generate_unique_code(db: Session) -> str:
    """Generate a unique 4-digit code for patient."""
    while True:
        code = ''.join(random.choices(string.digits, k=4))
        existing = db.query(Patient).filter(Patient.code == code).first()
        if not existing:
            return code


@router.post("/patients", response_model=CreatePatientResponse)
async def create_patient(
    request: CreatePatientRequest, 
    current_doctor: str = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    # Use the authenticated doctor from JWT token
    doctor_id = current_doctor

    # Check if email already exists
    existing = db.query(Patient).filter(Patient.email == request.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this email already exists")

    # Generate unique code
    code = generate_unique_code(db)

    # Create patient
    patient = Patient(
        id=str(uuid.uuid4()),
        email=request.email,
        name=request.name,
        status='pending',
        code=code
    )

    db.add(patient)

    # Create PatientDoctor relationship
    patient_doctor = PatientDoctor(
        patient_id=patient.id,
        doctor_id=current_doctor
    )
    db.add(patient_doctor)

    db.commit()
    db.refresh(patient)

    return CreatePatientResponse(message="Patient created successfully", code=code)