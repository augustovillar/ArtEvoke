"""
Unit tests for Session CRUD operations
Tests the creation, reading, updating, and deletion of sessions
"""
import pytest
from datetime import datetime
import uuid


class TestSessionCreation:
    """Test session creation functionality"""

    def test_create_session_with_valid_data(
        self, client, doctor_token, create_patient, link_doctor_patient
    ):
        """Test creating a session with valid data"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction",
                "interruption_time": 15
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["patient_id"] == create_patient.id
        assert data["mode"] == "memory_reconstruction"
        assert data["interruption_time"] == 15
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

    def test_create_session_with_art_exploration_mode(
        self, client, doctor_token, create_patient, link_doctor_patient
    ):
        """Test creating a session with art_exploration mode"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "art_exploration",
                "interruption_time": 20
            }
        )
        assert response.status_code == 201
        assert response.json()["mode"] == "art_exploration"

    def test_create_session_with_both_mode(
        self, client, doctor_token, create_patient, link_doctor_patient
    ):
        """Test creating a session with both modes"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "both",
                "interruption_time": 10
            }
        )
        assert response.status_code == 201
        assert response.json()["mode"] == "both"

    def test_create_session_with_default_interruption_time(
        self, client, doctor_token, create_patient, link_doctor_patient
    ):
        """Test that interruption_time defaults to 10 seconds"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction"
            }
        )
        assert response.status_code == 201
        assert response.json()["interruption_time"] == 10

    def test_create_session_for_nonexistent_patient(self, client, doctor_token):
        """Test creating a session for a non-existent patient"""
        fake_id = str(uuid.uuid4())
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": fake_id,
                "mode": "memory_reconstruction",
                "interruption_time": 10
            }
        )
        assert response.status_code == 404
        assert "Patient not found" in response.json()["detail"]


class TestSessionRetrieval:
    """Test session retrieval functionality"""

    def test_get_patient_sessions_returns_list(
        self, client, doctor_token, create_patient, link_doctor_patient, sample_session
    ):
        """Test getting all sessions for a patient"""
        response = client.get(
            f"/api/sessions/patient/{create_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == sample_session.id

    def test_get_patient_sessions_empty_list(
        self, client, doctor_token, create_patient, link_doctor_patient
    ):
        """Test getting sessions for patient with no sessions"""
        response = client.get(
            f"/api/sessions/patient/{create_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_sessions_as_patient(
        self, client, patient_token, sample_session
    ):
        """Test patient getting their own sessions"""
        response = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["status"] in ["pending", "in_progress"]

    def test_get_my_sessions_filters_completed(
        self, client, patient_token, db_session, sample_session
    ):
        """Test that my-sessions only shows pending and in_progress sessions"""
        # Update session to completed
        sample_session.status = "completed"
        db_session.commit()

        response = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_specific_session(self, client, doctor_token, sample_session):
        """Test getting a specific session by ID"""
        response = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_session.id
        assert data["mode"] == sample_session.mode

    def test_get_nonexistent_session(self, client, doctor_token):
        """Test getting a non-existent session"""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 404


class TestSessionUpdate:
    """Test session update functionality"""

    def test_update_session_to_in_progress(
        self, client, patient_token, sample_session
    ):
        """Test updating session status to in_progress"""
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_update_session_to_completed(
        self, client, patient_token, sample_session
    ):
        """Test updating session status to completed"""
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_update_session_with_started_at(
        self, client, patient_token, sample_session
    ):
        """Test updating session with started_at timestamp"""
        now = datetime.utcnow().isoformat()
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "in_progress",
                "started_at": now
            }
        )
        assert response.status_code == 200
        assert response.json()["started_at"] is not None

    def test_update_session_with_ended_at(
        self, client, patient_token, sample_session
    ):
        """Test updating session with ended_at timestamp"""
        now = datetime.utcnow().isoformat()
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "completed",
                "ended_at": now
            }
        )
        assert response.status_code == 200
        assert response.json()["ended_at"] is not None

    def test_update_session_link_memory_reconstruction(
        self, client, patient_token, sample_session
    ):
        """Test linking a memory reconstruction to session"""
        mr_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"memory_reconstruction_id": mr_id}
        )
        assert response.status_code == 200
        assert response.json()["memory_reconstruction_id"] == mr_id

    def test_update_session_link_art_exploration(
        self, client, patient_token, sample_session
    ):
        """Test linking an art exploration to session"""
        ae_id = str(uuid.uuid4())
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"art_exploration_id": ae_id}
        )
        assert response.status_code == 200
        assert response.json()["art_exploration_id"] == ae_id


class TestSessionDeletion:
    """Test session deletion functionality"""

    def test_delete_session(self, client, doctor_token, sample_session):
        """Test deleting a session"""
        response = client.delete(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 204

        # Verify session is deleted
        get_response = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert get_response.status_code == 404

    def test_delete_nonexistent_session(self, client, doctor_token):
        """Test deleting a non-existent session"""
        fake_id = str(uuid.uuid4())
        response = client.delete(
            f"/api/sessions/{fake_id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 404
