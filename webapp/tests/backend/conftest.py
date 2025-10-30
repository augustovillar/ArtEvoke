"""
Pytest configuration and fixtures for backend tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os

# Add FastAPI directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../FastAPI'))

from main import app
from orm.base import Base
from routes import get_db
from orm import Patient, Doctor, PatientDoctor, Session as SessionModel
from utils.auth import get_password_hash
import uuid
from datetime import datetime

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def doctor_data():
    """Sample doctor data"""
    return {
        "id": str(uuid.uuid4()),
        "email": "doctor@test.com",
        "password": get_password_hash("doctor123"),
        "name": "Dr. Test",
        "date_of_birth": datetime(1980, 1, 1).date(),
        "specialization": "Psychology",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def patient_data():
    """Sample patient data"""
    return {
        "id": str(uuid.uuid4()),
        "email": "patient@test.com",
        "password": get_password_hash("patient123"),
        "name": "Patient Test",
        "date_of_birth": datetime(1990, 1, 1).date(),
        "status": "active",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def another_patient_data():
    """Sample data for another patient"""
    return {
        "id": str(uuid.uuid4()),
        "email": "patient2@test.com",
        "password": get_password_hash("patient123"),
        "name": "Patient Two",
        "date_of_birth": datetime(1992, 5, 15).date(),
        "status": "active",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def another_doctor_data():
    """Sample data for another doctor"""
    return {
        "id": str(uuid.uuid4()),
        "email": "doctor2@test.com",
        "password": get_password_hash("doctor123"),
        "name": "Dr. Two",
        "date_of_birth": datetime(1985, 3, 20).date(),
        "specialization": "Psychiatry",
        "created_at": datetime.utcnow()
    }


@pytest.fixture
def create_doctor(db_session, doctor_data):
    """Create a doctor in the database"""
    doctor = Doctor(**doctor_data)
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def create_patient(db_session, patient_data):
    """Create a patient in the database"""
    patient = Patient(**patient_data)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def create_another_patient(db_session, another_patient_data):
    """Create another patient in the database"""
    patient = Patient(**another_patient_data)
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


@pytest.fixture
def create_another_doctor(db_session, another_doctor_data):
    """Create another doctor in the database"""
    doctor = Doctor(**another_doctor_data)
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)
    return doctor


@pytest.fixture
def link_doctor_patient(db_session, create_doctor, create_patient):
    """Create a relationship between doctor and patient"""
    relationship = PatientDoctor(
        patient_id=create_patient.id,
        doctor_id=create_doctor.id,
        created_at=datetime.utcnow()
    )
    db_session.add(relationship)
    db_session.commit()
    return relationship


@pytest.fixture
def doctor_token(client, create_doctor):
    """Get authentication token for doctor"""
    response = client.post(
        "/api/doctors/login",
        json={"email": "doctor@test.com", "password": "doctor123"}
    )
    return response.json()["token"]


@pytest.fixture
def patient_token(client, create_patient):
    """Get authentication token for patient"""
    response = client.post(
        "/api/patients/login",
        json={"email": "patient@test.com", "password": "patient123"}
    )
    return response.json()["token"]


@pytest.fixture
def another_doctor_token(client, create_another_doctor):
    """Get authentication token for another doctor"""
    response = client.post(
        "/api/doctors/login",
        json={"email": "doctor2@test.com", "password": "doctor123"}
    )
    return response.json()["token"]


@pytest.fixture
def sample_session(db_session, create_doctor, create_patient, link_doctor_patient):
    """Create a sample session"""
    session = SessionModel(
        id=str(uuid.uuid4()),
        patient_id=create_patient.id,
        doctor_id=create_doctor.id,
        mode="memory_reconstruction",
        interruption_time=10,
        status="pending",
        created_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session
