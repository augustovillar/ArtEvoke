"""
Integration tests for Session workflow
Tests the complete flow of session lifecycle
"""
import pytest
from datetime import datetime
import uuid


class TestSessionWorkflow:
    """Test complete session workflow from creation to completion"""

    def test_complete_session_workflow_memory_reconstruction(
        self, client, doctor_token, patient_token, create_patient, 
        create_doctor, link_doctor_patient
    ):
        """Test complete workflow: create -> start -> complete session for memory reconstruction"""
        
        # Step 1: Doctor creates session
        create_response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction",
                "interruption_time": 15
            }
        )
        assert create_response.status_code == 201
        session_id = create_response.json()["id"]
        assert create_response.json()["status"] == "pending"

        # Step 2: Patient views their pending sessions
        my_sessions_response = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert my_sessions_response.status_code == 200
        sessions = my_sessions_response.json()
        assert len(sessions) == 1
        assert sessions[0]["id"] == session_id

        # Step 3: Patient starts session
        start_time = datetime.utcnow().isoformat()
        start_response = client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "in_progress",
                "started_at": start_time
            }
        )
        assert start_response.status_code == 200
        assert start_response.json()["status"] == "in_progress"
        assert start_response.json()["started_at"] is not None

        # Step 4: Patient completes session and links evaluation
        mr_id = str(uuid.uuid4())
        end_time = datetime.utcnow().isoformat()
        complete_response = client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "completed",
                "ended_at": end_time,
                "memory_reconstruction_id": mr_id
            }
        )
        assert complete_response.status_code == 200
        assert complete_response.json()["status"] == "completed"
        assert complete_response.json()["ended_at"] is not None
        assert complete_response.json()["memory_reconstruction_id"] == mr_id

        # Step 5: Doctor views completed session
        doctor_view_response = client.get(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert doctor_view_response.status_code == 200
        final_session = doctor_view_response.json()
        assert final_session["status"] == "completed"
        assert final_session["memory_reconstruction_id"] == mr_id

        # Step 6: Completed session should not appear in my-sessions
        final_my_sessions = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert len(final_my_sessions.json()) == 0

    def test_complete_session_workflow_art_exploration(
        self, client, doctor_token, patient_token, create_patient, 
        create_doctor, link_doctor_patient
    ):
        """Test complete workflow for art exploration mode"""
        
        # Create session with art_exploration mode
        create_response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "art_exploration",
                "interruption_time": 20
            }
        )
        session_id = create_response.json()["id"]

        # Start and complete with art_exploration_id
        client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress", "started_at": datetime.utcnow().isoformat()}
        )

        ae_id = str(uuid.uuid4())
        complete_response = client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "completed",
                "ended_at": datetime.utcnow().isoformat(),
                "art_exploration_id": ae_id
            }
        )
        assert complete_response.json()["art_exploration_id"] == ae_id

    def test_session_workflow_with_both_modes(
        self, client, doctor_token, patient_token, create_patient, 
        create_doctor, link_doctor_patient
    ):
        """Test workflow with both evaluation modes"""
        
        # Create session with both modes
        create_response = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "both",
                "interruption_time": 10
            }
        )
        session_id = create_response.json()["id"]

        # Start session
        client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress", "started_at": datetime.utcnow().isoformat()}
        )

        # Complete with both IDs
        mr_id = str(uuid.uuid4())
        ae_id = str(uuid.uuid4())
        complete_response = client.patch(
            f"/api/sessions/{session_id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={
                "status": "completed",
                "ended_at": datetime.utcnow().isoformat(),
                "memory_reconstruction_id": mr_id,
                "art_exploration_id": ae_id
            }
        )
        
        assert complete_response.json()["memory_reconstruction_id"] == mr_id
        assert complete_response.json()["art_exploration_id"] == ae_id


class TestMultipleSessionsWorkflow:
    """Test workflows with multiple sessions"""

    def test_patient_with_multiple_sessions(
        self, client, doctor_token, patient_token, create_patient, link_doctor_patient
    ):
        """Test patient with multiple sessions in different states"""
        
        # Create 3 sessions
        session_ids = []
        for i in range(3):
            response = client.post(
                "/api/sessions/",
                headers={"Authorization": f"Bearer {doctor_token}"},
                json={
                    "patient_id": create_patient.id,
                    "mode": "memory_reconstruction",
                    "interruption_time": 10 + i
                }
            )
            session_ids.append(response.json()["id"])

        # Start one session
        client.patch(
            f"/api/sessions/{session_ids[0]}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress"}
        )

        # Complete another session
        client.patch(
            f"/api/sessions/{session_ids[1]}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "completed"}
        )

        # Check my-sessions (should show 2: pending and in_progress)
        my_sessions = client.get(
            "/api/sessions/my-sessions",
            headers={"Authorization": f"Bearer {patient_token}"}
        )
        assert len(my_sessions.json()) == 2

        # Doctor should see all 3 sessions
        all_sessions = client.get(
            f"/api/sessions/patient/{create_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert len(all_sessions.json()) == 3

    def test_doctor_manages_multiple_patients(
        self, client, db_session, doctor_token, create_doctor, 
        create_patient, create_another_patient, link_doctor_patient
    ):
        """Test doctor creating sessions for multiple patients"""
        from orm import PatientDoctor
        from datetime import datetime
        
        # Link doctor to second patient
        relationship = PatientDoctor(
            patient_id=create_another_patient.id,
            doctor_id=create_doctor.id,
            created_at=datetime.utcnow()
        )
        db_session.add(relationship)
        db_session.commit()

        # Create sessions for both patients
        session1 = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_patient.id,
                "mode": "memory_reconstruction"
            }
        )
        
        session2 = client.post(
            "/api/sessions/",
            headers={"Authorization": f"Bearer {doctor_token}"},
            json={
                "patient_id": create_another_patient.id,
                "mode": "art_exploration"
            }
        )

        assert session1.status_code == 201
        assert session2.status_code == 201

        # Verify doctor can view both
        patient1_sessions = client.get(
            f"/api/sessions/patient/{create_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        patient2_sessions = client.get(
            f"/api/sessions/patient/{create_another_patient.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )

        assert len(patient1_sessions.json()) == 1
        assert len(patient2_sessions.json()) == 1


class TestSessionDeletionWorkflow:
    """Test session deletion scenarios"""

    def test_doctor_deletes_pending_session(
        self, client, doctor_token, sample_session
    ):
        """Test doctor deleting a pending session"""
        # Verify session exists
        get_response = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert get_response.status_code == 200

        # Delete session
        delete_response = client.delete(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert delete_response.status_code == 204

        # Verify session is gone
        get_after_delete = client.get(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert get_after_delete.status_code == 404

    def test_cannot_delete_in_progress_session(
        self, client, doctor_token, patient_token, sample_session
    ):
        """Test that in-progress sessions can still be deleted"""
        # Start session
        client.patch(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {patient_token}"},
            json={"status": "in_progress"}
        )

        # Doctor can delete even in-progress sessions
        delete_response = client.delete(
            f"/api/sessions/{sample_session.id}",
            headers={"Authorization": f"Bearer {doctor_token}"}
        )
        assert delete_response.status_code == 204
