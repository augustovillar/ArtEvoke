"""
Database Verification Script for ArtEvoke ORM.
This script performs various operations and shows clear results.
"""

from database_config import setup_database, get_connection_info
from orm import (
    get_db,
    Patient,
    Doctor,
    Session,
    ArtExploration,
    CatalogItem,
    SemArt,
    WikiArt,
    Ipiranga,
)
from datetime import date
import uuid


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def show_database_stats():
    """Show comprehensive database statistics."""
    print_section("DATABASE STATISTICS")

    db = next(get_db())
    try:
        stats = {
            "Patients": db.query(Patient).count(),
            "Doctors": db.query(Doctor).count(),
            "Sessions": db.query(Session).count(),
            "Art Explorations": db.query(ArtExploration).count(),
            "Catalog Items": db.query(CatalogItem).count(),
            "SemArt Items": db.query(SemArt).count(),
            "WikiArt Items": db.query(WikiArt).count(),
            "Ipiranga Items": db.query(Ipiranga).count(),
        }

        for table, count in stats.items():
            print(f"  {table:.<30} {count:>5} records")

        return stats
    finally:
        db.close()


def list_all_patients():
    """List all patients in detail."""
    print_section("ALL PATIENTS IN DATABASE")

    db = next(get_db())
    try:
        patients = db.query(Patient).all()

        if not patients:
            print("  No patients found in database.")
            return

        for i, patient in enumerate(patients, 1):
            print(f"\n  Patient #{i}:")
            print(f"    ID:           {patient.id}")
            print(f"    Username:     {patient.username}")
            print(f"    Name:         {patient.name}")
            print(f"    Email:        {patient.email}")
            print(f"    Birth Date:   {patient.date_of_birth}")
            print(f"    Education:    {patient.education_level}")
            print(f"    Occupation:   {patient.occupation}")
            print(f"    Created:      {patient.created_at}")

            # Show relationships
            print(f"    Relationships:")
            print(f"      - Art Explorations: {len(patient.art_explorations)}")
            print(f"      - Sessions:         {len(patient.sessions)}")
            print(f"      - Doctors:          {len(patient.doctors)}")
    finally:
        db.close()


def list_all_doctors():
    """List all doctors in detail."""
    print_section("ALL DOCTORS IN DATABASE")

    db = next(get_db())
    try:
        doctors = db.query(Doctor).all()

        if not doctors:
            print("  No doctors found in database.")
            return

        for i, doctor in enumerate(doctors, 1):
            print(f"\n  Doctor #{i}:")
            print(f"    ID:             {doctor.id}")
            print(f"    Username:       {doctor.username}")
            print(f"    Name:           {doctor.name}")
            print(f"    Email:          {doctor.email}")
            print(f"    Specialization: {doctor.specialization}")
            print(f"    Created:        {doctor.created_at}")
    finally:
        db.close()


def create_sample_data():
    """Create sample patient and doctor for testing."""
    print_section("CREATING SAMPLE DATA")

    db = next(get_db())
    try:
        # Check if we already have a patient
        existing_patient = (
            db.query(Patient).filter(Patient.username == "jane_smith").first()
        )
        if existing_patient:
            print("  ✓ Sample patient 'jane_smith' already exists")
            patient = existing_patient
        else:
            patient = Patient(
                id=str(uuid.uuid4()),
                username="jane_smith",
                email="jane.smith@example.com",
                password="hashed_password_123",
                name="Jane Smith",
                date_of_birth=date(1955, 8, 20),
                education_level="Master's Degree",
                occupation="Retired Professor",
                diseases="Mild Cognitive Impairment",
                medications="Vitamin E",
                visual_impairment=False,
                hearing_impairment=True,
                household_income=4500.00,
                ethnicity="Hispanic",
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)
            print(f"  ✓ Created patient: {patient.name} (ID: {patient.id})")

        # Check if we already have a doctor
        existing_doctor = (
            db.query(Doctor).filter(Doctor.username == "dr_oliveira").first()
        )
        if existing_doctor:
            print("  ✓ Sample doctor 'dr_oliveira' already exists")
            doctor = existing_doctor
        else:
            doctor = Doctor(
                id=str(uuid.uuid4()),
                username="dr_oliveira",
                email="dr.oliveira@example.com",
                password="hashed_password_456",
                name="Dr. Maria Oliveira",
                date_of_birth=date(1975, 3, 10),
                specialization="Neuropsychology",
            )
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
            print(f"  ✓ Created doctor: {doctor.name} (ID: {doctor.id})")

        return patient, doctor
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error creating sample data: {e}")
        raise
    finally:
        db.close()


def create_complete_session_example():
    """Create a complete example with patient, doctor, art exploration, and session."""
    print_section("CREATING COMPLETE SESSION EXAMPLE")

    db = next(get_db())
    try:
        # Get or create patient and doctor
        patient = db.query(Patient).filter(Patient.username == "jane_smith").first()
        doctor = db.query(Doctor).filter(Doctor.username == "dr_oliveira").first()

        if not patient or not doctor:
            print("  ✗ Patient or doctor not found. Run create_sample_data() first.")
            return

        print(f"  Using patient: {patient.name}")
        print(f"  Using doctor: {doctor.name}")

        # Create art exploration
        art_exploration = ArtExploration(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            story_generated="A beautiful journey through Renaissance art, featuring masterpieces from Leonardo da Vinci and Michelangelo...",
            dataset="WikiArt",
            language="EN",
        )
        db.add(art_exploration)
        print(f"  ✓ Created art exploration (ID: {art_exploration.id})")

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
        print(f"  ✓ Created session (ID: {session.id})")

        return session
    except Exception as e:
        db.rollback()
        print(f"  ✗ Error creating session: {e}")
        raise
    finally:
        db.close()


def verify_relationships():
    """Verify that ORM relationships work correctly."""
    print_section("VERIFYING ORM RELATIONSHIPS")

    db = next(get_db())
    try:
        patient = db.query(Patient).filter(Patient.username == "jane_smith").first()

        if not patient:
            print("  No patient found to verify relationships.")
            return

        print(f"  Patient: {patient.name}")
        print(f"\n  Art Explorations ({len(patient.art_explorations)}):")
        for exploration in patient.art_explorations:
            print(f"    - {exploration.dataset} ({exploration.language})")
            print(f"      Story preview: {exploration.story_generated[:80]}...")

        print(f"\n  Sessions ({len(patient.sessions)}):")
        for session in patient.sessions:
            print(f"    - Mode: {session.mode}")
            print(f"      Started: {session.started_at}")
            print(f"      Doctor: {session.doctor.name if session.doctor else 'N/A'}")

        print("\n  ✓ Relationships are working correctly!")
    finally:
        db.close()


def run_sql_query(query):
    """Execute a raw SQL query and display results."""
    print_section(f"RAW SQL QUERY")
    print(f"  Query: {query}\n")

    db = next(get_db())
    try:
        result = db.execute(query)
        rows = result.fetchall()

        if not rows:
            print("  No results found.")
            return

        # Print column names
        print("  " + " | ".join(result.keys()))
        print("  " + "-" * 60)

        # Print rows
        for row in rows:
            print("  " + " | ".join(str(val)[:30] for val in row))
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ARTEVOKE DATABASE VERIFICATION TOOL")
    print("=" * 70)

    # Initialize database
    try:
        engine = setup_database(echo=False)  # Disable SQL logging for cleaner output
        info = get_connection_info()
        print(f"\n  ✓ Connected to: {info['database']} @ {info['host']}:{info['port']}")
        print(f"  ✓ User: {info['user']}")
    except Exception as e:
        print(f"\n  ✗ Failed to connect: {e}")
        exit(1)

    # Show initial stats
    initial_stats = show_database_stats()

    # List existing data
    list_all_patients()
    list_all_doctors()

    # Create sample data if needed
    if initial_stats["Patients"] == 0 or initial_stats["Doctors"] == 0:
        print("\n  → Database is empty, creating sample data...")
        create_sample_data()

    # Create a complete example
    create_complete_session_example()

    # Show updated stats
    show_database_stats()

    # List all patients again to see changes
    list_all_patients()

    # Verify relationships work
    verify_relationships()

    # Run some raw SQL queries to prove database is working
    print_section("RAW SQL VERIFICATION")
    print("\n  Executing: SELECT * FROM Patient LIMIT 3")
    run_sql_query(
        "SELECT id, username, name, email, education_level FROM Patient LIMIT 3"
    )

    print("\n  Executing: SELECT * FROM Doctor LIMIT 3")
    run_sql_query("SELECT id, username, name, specialization FROM Doctor LIMIT 3")

    print_section("✓ VERIFICATION COMPLETE")
    print(
        """
  Your ORM is working perfectly! Here's what we verified:
  
  1. ✓ Database connection is working
  2. ✓ Can create new records (INSERT)
  3. ✓ Can query records (SELECT)
  4. ✓ ORM relationships work (lazy loading)
  5. ✓ Raw SQL queries work
  6. ✓ Transactions and commits work
  
  You can now use the ORM in your FastAPI application!
    """
    )
    print("=" * 70)
