"""
Unit tests for Session routes - Authentication and Authorization
Tests the security and access control of session endpoints
"""
import pytest
from datetime import datetime


class TestSessionAuthentication:
    """Test authentication requirements for session endpoints"""

    def test_create_session_requires_authentication(self, client, create_patient, create_doctor, link_doctor_patient):
        """Test that creating a session requires authentication"""
        response = client.post(
            "/api/sessions/",
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction",
                "interruption_time": 10
            }
        )
        assert response.status_code == 401

    def test_get_patient_sessions_requires_authentication(self, client, create_patient):
        """Test that getting patient sessions requires authentication"""
        response = client.get(f"/api/sessions/patient/{create_patient.id}")
        assert response.status_code == 401

    def test_get_my_sessions_requires_authentication(self, client):
        """Test that getting own sessions requires authentication"""
        response = client.get("/api/sessions/my-sessions")
        assert response.status_code == 401

    def test_get_session_requires_authentication(self, client, sample_session):
        """Test that getting a specific session requires authentication"""
        response = client.get(f"/api/sessions/{sample_session.id}")
        assert response.status_code == 401

    def test_update_session_requires_authentication(self, client, sample_session):
        """Test that updating a session requires authentication"""
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            json={"status": "in_progress"}
        )
        assert response.status_code == 401

    def test_delete_session_requires_authentication(self, client, sample_session):
        """Test that deleting a session requires authentication"""
        response = client.delete(f"/api/sessions/{sample_session.id}")
        assert response.status_code == 401


class TestSessionAuthorization:
    """Test authorization rules for session endpoints"""

    def test_only_doctor_can_create_session(self, client, patient_token, create_patient):
        """Test that only doctors can create sessions"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction",
                "interruption_time": 10
            }
        )
        assert response.status_code == 403
        assert "Only doctors" in response.json()["detail"]

    def test_doctor_cannot_create_session_for_unlinked_patient(
        self, client, doctor_token, create_another_patient
    ):
        """Test that doctor cannot create session for patient they don't have access to"""
        response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_another_patient.id,
                "mode": "memory_reconstruction",
                "interruption_time": 10
            }
        )
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"]

    def test_doctor_can_only_view_linked_patient_sessions(
        self, client, doctor_token, create_another_patient
    ):
        """Test that doctor can only view sessions of linked patients"""
        response = client.get(
            f"/api/sessions/patient/{create_another_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 403
        assert "don't have access" in response.json()["detail"]

    def test_patient_cannot_view_other_patient_sessions(
        self, client, patient_token, create_another_patient
    ):
        """Test that patient cannot view another patient's sessions"""
        response = client.get(
            f"/api/sessions/patient/{create_another_patient.id}",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 403

    def test_doctor_cannot_delete_other_doctor_session(
        self, client, another_doctor_token, sample_session
    ):
        """Test that doctor cannot delete sessions created by another doctor"""
        response = client.delete(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {another_doctor_token}"}
        )
        assert response.status_code == 403

    def test_patient_can_view_own_sessions(self, client, patient_token):
        """Test that patient can view their own sessions"""
        response = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestSessionAccessControl:
    """Test fine-grained access control for sessions"""

    def test_patient_can_view_session_they_are_part_of(
        self, client, patient_token, sample_session
    ):
        """Test that patient can view a session they are part of"""
        response = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == sample_session.id

    def test_doctor_can_view_session_they_created(
        self, client, doctor_token, sample_session
    ):
        """Test that doctor can view a session they created"""
        response = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == sample_session.id

    def test_patient_can_update_own_session(
        self, client, patient_token, sample_session
    ):
        """Test that patient can update their own session status"""
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_doctor_cannot_update_session_status(
        self, client, doctor_token, sample_session
    ):
        """Test that doctor cannot update session status (only patient can)"""
        response = client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={"status": "in_progress"}
        )
        assert response.status_code == 403
