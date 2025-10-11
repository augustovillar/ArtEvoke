"""
Example usage of the ArtEvoke ORM models.
This file demonstrates how to initialize the database and use the models.

To run these examples:
1. Ensure Docker MySQL is running: cd /home/augustovillar/ArtEvoke/webapp/data/db && docker-compose up -d
2. Install requirements: pip install -r requirements.txt
3. Run this file: python orm_examples.py
"""

from database_config import setup_database, get_connection_info
from orm import (
    get_db,
    Patient,
    Doctor,
    Session,
    ArtExploration,
)
from datetime import date
import uuid


def initialize_database():
    """
    Initialize the database connection.
    Uses the Docker MySQL configuration from database_config.py
    """
    # Docker MySQL connection (from docker-compose.yml and .env.mysql)
    # This uses the centralized database_config module
    engine = setup_database(echo=True)

    print(f"Connected to: {get_connection_info()['url']}")
    return engine


def example_create_patient():
    """Example: Create a new patient (or return existing if already created)."""
    db = next(get_db())

    try:
        # Check if patient already exists
        existing_patient = (
            db.query(Patient).filter(Patient.email == "john@example.com").first()
        )
        if existing_patient:
            print(
                f"✓ Patient already exists: {existing_patient.name} (ID: {existing_patient.id})"
            )
            return existing_patient

        # Create new patient
        new_patient = Patient(
            id=str(uuid.uuid4()),
            username="john_doe",
            email="john@example.com",
            password="hashed_password_here",  # Remember to hash passwords!
            name="John Doe",
            date_of_birth=date(1950, 5, 15),
            education_level="Bachelor's Degree",
            occupation="Retired Teacher",
            diseases="Alzheimer's Disease",
            medications="Donepezil",
            visual_impairment=False,
            hearing_impairment=False,
            household_income=3000.00,
            ethnicity="Caucasian",
        )

        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)

        print(f"✓ Created new patient: {new_patient.name} (ID: {new_patient.id})")
        return new_patient
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating patient: {e}")
        return None
    finally:
        db.close()


def example_query_patients():
    """Example: Query patients."""
    db = next(get_db())

    try:
        # Get all patients
        patients = db.query(Patient).all()
        print(f"Found {len(patients)} patients")

        # Filter by education level
        bachelor_patients = (
            db.query(Patient)
            .filter(Patient.education_level == "Bachelor's Degree")
            .all()
        )
        print(f"Found {len(bachelor_patients)} patients with Bachelor's Degree")

        # Get patient with relationships
        patient = db.query(Patient).first()
        if patient:
            print(f"Patient: {patient.name}")
            print(f"Art Explorations: {len(patient.art_explorations)}")
            print(f"Sessions: {len(patient.sessions)}")

        return patients
    finally:
        db.close()


def example_create_session_with_art_exploration():
    """Example: Create a session with art exploration."""
    db = next(get_db())

    try:
        # Assume we have a patient and doctor already
        patient = db.query(Patient).first()
        doctor = db.query(Doctor).first()

        if not patient or not doctor:
            print("Need to create patient and doctor first")
            return

        # Create art exploration
        art_exploration = ArtExploration(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            story_generated="Once upon a time, there was a beautiful painting...",
            dataset="WikiArt",
            language="EN",
        )

        db.add(art_exploration)

        # Create session
        session = Session(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            doctor_id=doctor.id,
            art_exploration_id=art_exploration.id,
            mode="art_exploration",
            started_at=date.today(),
        )

        db.add(session)
        db.commit()

        print(f"Created session: {session}")
        return session
    except Exception as e:
        db.rollback()
        print(f"Error creating session: {e}")
        raise
    finally:
        db.close()


def example_fastapi_endpoint():
    """
    Example FastAPI endpoint using the ORM.
    Add this to your main.py file.
    """
    from fastapi import FastAPI, Depends
    from sqlalchemy.orm import Session as DBSession
    from orm import get_db, Patient

    app = FastAPI()

    @app.get("/patients")
    def get_patients(db: DBSession = Depends(get_db)):
        """Get all patients."""
        patients = db.query(Patient).all()
        return patients

    @app.get("/patients/{patient_id}")
    def get_patient(patient_id: str, db: DBSession = Depends(get_db)):
        """Get a specific patient."""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            return {"error": "Patient not found"}
        return patient

    @app.post("/patients")
    def create_patient(patient_data: dict, db: DBSession = Depends(get_db)):
        """Create a new patient."""
        new_patient = Patient(id=str(uuid.uuid4()), **patient_data)
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient


if __name__ == "__main__":
    print("=" * 60)
    print("ArtEvoke ORM Examples")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database connection...")
    try:
        engine = initialize_database()
        print("✓ Database connected successfully!")
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        print("\nMake sure Docker MySQL is running:")
        print("  cd /home/augustovillar/ArtEvoke/webapp/data/db")
        print("  docker-compose up -d")
        exit(1)

    print("\n2. Testing database connection...")
    try:
        db = next(get_db())
        patient_count = db.query(Patient).count()
        doctor_count = db.query(Doctor).count()
        print("✓ Database is accessible!")
        print(f"  - Patients in database: {patient_count}")
        print(f"  - Doctors in database: {doctor_count}")
        db.close()
    except Exception as e:
        print(f"✗ Error querying database: {e}")
        exit(1)

    print("\n" + "=" * 60)
    print("Examples available:")
    print("=" * 60)
    print("- example_create_patient() - Create or get existing patient")
    print("- example_query_patients() - Query and filter patients")
    print("- example_create_session_with_art_exploration() - Create session")
    print("\nConnection: mysql+pymysql://appuser:***@localhost:3306/appdb")

    # Run examples
    print("\n3. Creating/getting patient...")
    patient = example_create_patient()

    if patient:
        print("\n4. Querying patients...")
        example_query_patients()

        print("\n5. Creating session with art exploration...")
        example_create_session_with_art_exploration()

    print("\n" + "=" * 60)
    print("✓ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 60)
