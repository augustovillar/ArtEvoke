# Backend Tests - Session Management System

## Overview

This directory contains comprehensive unit and integration tests for the Session Management System backend API.

## Test Structure

```
tests/backend/
├── conftest.py                 # Pytest fixtures and configuration
├── test_session_auth.py        # Authentication & Authorization tests
├── test_session_crud.py        # CRUD operation tests
├── test_session_workflow.py    # Integration workflow tests
└── requirements.txt            # Testing dependencies
```

## Test Coverage

### 1. Authentication Tests (`test_session_auth.py`)
- **Authentication Requirements**: All endpoints require valid JWT tokens
- **Authorization Rules**: Role-based access control (doctor vs patient)
- **Access Control**: Fine-grained permissions per session

**Key Test Cases:**
- ✅ Unauthenticated requests are rejected (401)
- ✅ Only doctors can create sessions
- ✅ Doctors can only access sessions of linked patients
- ✅ Patients can only view their own sessions
- ✅ Session updates are restricted to session participants

### 2. CRUD Tests (`test_session_crud.py`)
- **Create**: Session creation with various configurations
- **Read**: Retrieving sessions (list and individual)
- **Update**: Status changes and field updates
- **Delete**: Session deletion by authorized users

**Key Test Cases:**
- ✅ Create sessions with different modes (memory_reconstruction, art_exploration, both)
- ✅ Default interruption_time is 10 seconds
- ✅ List sessions by patient (doctor view)
- ✅ List own sessions (patient view, excludes completed)
- ✅ Update session status (pending → in_progress → completed)
- ✅ Link evaluations to sessions
- ✅ Delete sessions (doctor only)

### 3. Workflow Tests (`test_session_workflow.py`)
- **Complete Workflows**: End-to-end session lifecycle
- **Multiple Sessions**: Managing multiple concurrent sessions
- **Multiple Patients**: Doctor working with multiple patients

**Key Test Cases:**
- ✅ Complete workflow: create → start → complete
- ✅ Sessions with different modes
- ✅ Patient with multiple sessions in different states
- ✅ Doctor managing sessions for multiple patients
- ✅ Session deletion workflows

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Install FastAPI dependencies (from FastAPI directory):
```bash
cd ../../FastAPI
pip install -r requirements.txt
```

### Run All Tests

```bash
# From webapp/tests/backend directory
pytest -v

# With coverage report
pytest --cov=../../FastAPI --cov-report=html -v

# Run specific test file
pytest test_session_auth.py -v

# Run specific test class
pytest test_session_auth.py::TestSessionAuthentication -v

# Run specific test
pytest test_session_auth.py::TestSessionAuthentication::test_create_session_requires_authentication -v
```

### Test Output

```
tests/backend/test_session_auth.py::TestSessionAuthentication::test_create_session_requires_authentication PASSED
tests/backend/test_session_auth.py::TestSessionAuthentication::test_get_patient_sessions_requires_authentication PASSED
tests/backend/test_session_auth.py::TestSessionAuthorization::test_only_doctor_can_create_session PASSED
...
========================= 45 passed in 2.34s =========================
```

## Test Database

Tests use an in-memory SQLite database that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Isolated from production data

## Fixtures

### User Fixtures
- `doctor_data`: Sample doctor data
- `patient_data`: Sample patient data
- `create_doctor`: Creates and returns a doctor
- `create_patient`: Creates and returns a patient
- `link_doctor_patient`: Links doctor and patient in PatientDoctor table

### Authentication Fixtures
- `doctor_token`: JWT token for doctor
- `patient_token`: JWT token for patient

### Session Fixtures
- `sample_session`: Creates a sample pending session

## Adding New Tests

1. Add test functions to appropriate test file
2. Use descriptive test names: `test_<what_it_tests>`
3. Follow AAA pattern: Arrange, Act, Assert
4. Use existing fixtures when possible

Example:
```python
def test_new_feature(client, doctor_token, sample_session):
    """Test description"""
    # Arrange
    data = {"field": "value"}
    
    # Act
    response = client.post(
        "/api/endpoint",
        headers={"Authorization": f"Bearer {doctor_token}"},
        json=data
    )
    
    # Assert
    assert response.status_code == 200
    assert response.json()["field"] == "value"
```

## Continuous Integration

These tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

## Coverage Goals

- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Critical Paths**: 100%

## Troubleshooting

### Import Errors
If you get import errors, ensure FastAPI directory is in Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:../../FastAPI"
```

### Database Errors
If tests fail with database errors, check that:
- SQLAlchemy models are properly imported
- Relationships are correctly defined
- Foreign keys are valid

### Token Errors
If authentication fails:
- Check JWT_SECRET is set
- Verify password hashing matches login implementation
- Ensure tokens are properly formatted
