#!/usr/bin/env python3
"""
Comprehensive test for the complete HR Avatar workflow
Tests the entire flow from HR creating a vacancy to candidate completing an interview
"""

import pytest
import asyncio
import json
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import the FastAPI app
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.vacancy import Vacancy
from app.models.interview_link import InterviewLink
from app.services.auth import AuthService


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def hr_user(client):
    """Create HR user for testing"""
    user_data = {
        "email": "hr@test.com",
        "password": "password123",
        "full_name": "HR Manager"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Login to get token
    login_data = {
        "email": "hr@test.com",
        "password": "password123"
    }
    
    response = client.post("/api/v1/auth/login-json", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {
        "user_data": user_data,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def mock_services():
    """Mock external services"""
    with patch('app.services.speech_to_text.SpeechToTextService') as mock_stt, \
         patch('app.services.ai_analysis.AIAnalysisService') as mock_ai, \
         patch('app.services.text_to_speech.TextToSpeechService') as mock_tts, \
         patch('app.services.scoring.ScoringService') as mock_scoring:
        
        # Configure mocks
        mock_stt.return_value.is_available.return_value = True
        mock_stt.return_value.transcribe.return_value = "Test transcription"
        
        mock_ai.return_value.is_available.return_value = True
        mock_ai.return_value.analyze_response.return_value = {
            "score": 8.5,
            "feedback": "Good response",
            "analysis": {"clarity": 9, "relevance": 8}
        }
        
        mock_tts.return_value.is_available.return_value = True
        mock_tts.return_value.generate_speech.return_value = b"fake_audio_data"
        
        mock_scoring.return_value.is_available.return_value = True
        mock_scoring.return_value.calculate_score.return_value = 8.5
        
        yield {
            "stt": mock_stt,
            "ai": mock_ai,
            "tts": mock_tts,
            "scoring": mock_scoring
        }


class TestCompleteWorkflow:
    """Test the complete HR Avatar workflow"""
    
    def test_complete_workflow(self, client, hr_user, mock_services):
        """Test the complete workflow from vacancy creation to interview completion"""
        
        # Step 1: HR creates a vacancy
        vacancy_data = {
            "title": "Python Developer",
            "description": "We are looking for a Python developer",
            "requirements": "Python, FastAPI, SQLAlchemy",
            "responsibilities": "Develop web applications",
            "company_name": "Test Company",
            "location": "Remote",
            "salary_range": "100000-150000",
            "employment_type": "full-time",
            "experience_level": "middle"
        }
        
        response = client.post(
            "/api/v1/vacancies/",
            json=vacancy_data,
            headers=hr_user["headers"]
        )
        assert response.status_code == 201
        vacancy = response.json()
        vacancy_id = vacancy["id"]
        
        print(f"✅ Step 1: Vacancy created with ID {vacancy_id}")
        
        # Step 2: HR uploads a document for the vacancy
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Job description content for Python Developer position...")
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("job_description.txt", f, "text/plain")}
                response = client.post(
                    f"/api/v1/vacancies/{vacancy_id}/upload-document",
                    files=files,
                    headers=hr_user["headers"]
                )
                assert response.status_code == 200
                upload_result = response.json()
                assert upload_result["status"] == "pending"
                
            print(f"✅ Step 2: Document uploaded for vacancy {vacancy_id}")
            
            # Step 3: HR processes the document (mock processing)
            response = client.post(
                f"/api/v1/vacancies/{vacancy_id}/process-document",
                headers=hr_user["headers"]
            )
            assert response.status_code == 200
            process_result = response.json()
            assert process_result["status"] == "completed"
            
            print(f"✅ Step 3: Document processed for vacancy {vacancy_id}")
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        # Step 4: HR creates an interview link for a candidate
        link_data = {
            "candidate_name": "John Doe",
            "candidate_email": "john.doe@example.com",
            "candidate_phone": "+1-555-0123",
            "candidate_notes": "Experienced Python developer",
            "expires_hours": 6
        }
        
        response = client.post(
            f"/api/v1/interview-links/?vacancy_id={vacancy_id}",
            json=link_data,
            headers=hr_user["headers"]
        )
        assert response.status_code == 201
        interview_link = response.json()
        link_token = interview_link["unique_token"]
        link_id = interview_link["id"]
        
        print(f"✅ Step 4: Interview link created with token {link_token[:10]}...")
        
        # Step 5: Candidate accesses the link (without authentication)
        response = client.get(f"/api/v1/candidate/access/{link_token}")
        assert response.status_code == 200
        access_info = response.json()
        assert access_info["vacancy_title"] == "Python Developer"
        assert access_info["company_name"] == "Test Company"
        assert not access_info["is_expired"]
        assert not access_info["is_used"]
        
        print(f"✅ Step 5: Candidate accessed link successfully")
        
        # Step 6: Candidate registers for the interview
        candidate_data = {
            "candidate_name": "John Doe",
            "candidate_email": "john.doe@example.com",
            "candidate_phone": "+1-555-0123"
        }
        
        response = client.post(
            f"/api/v1/candidate/access/{link_token}/register",
            json=candidate_data
        )
        assert response.status_code == 200
        session_info = response.json()
        session_id = session_info["session_id"]
        
        print(f"✅ Step 6: Candidate registered with session {session_id[:10]}...")
        
        # Step 7: Candidate uploads resume
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("John Doe's resume content...")
            resume_path = f.name
        
        try:
            with open(resume_path, 'rb') as f:
                files = {"file": ("resume.txt", f, "text/plain")}
                response = client.post(
                    f"/api/v1/candidate/access/{link_token}/upload-resume",
                    files=files
                )
                assert response.status_code == 200
                
            print(f"✅ Step 7: Candidate uploaded resume")
            
        finally:
            if os.path.exists(resume_path):
                os.unlink(resume_path)
        
        # Step 8: Candidate gets vacancy information
        response = client.get(f"/api/v1/candidate/session/{session_id}/vacancy-info")
        assert response.status_code == 200
        vacancy_info = response.json()
        assert vacancy_info["title"] == "Python Developer"
        assert vacancy_info["company_name"] == "Test Company"
        
        print(f"✅ Step 8: Candidate retrieved vacancy information")
        
        # Step 9: Check session status
        response = client.get(f"/api/v1/candidate/session/{session_id}/status")
        assert response.status_code == 200
        status_info = response.json()
        assert status_info["is_active"]
        assert not status_info["is_expired"]
        assert status_info["candidate_name"] == "John Doe"
        
        print(f"✅ Step 9: Session status checked")
        
        # Step 10: Mock interview process (WebSocket simulation)
        # In a real scenario, this would be done through WebSocket
        # For testing, we'll simulate the interview completion
        
        # Step 11: Candidate completes the interview
        response = client.post(f"/api/v1/candidate/session/{session_id}/complete")
        assert response.status_code == 200
        completion_info = response.json()
        assert "completed_at" in completion_info
        
        print(f"✅ Step 10: Interview completed")
        
        # Step 11: HR checks interview link statistics
        response = client.get(
            f"/api/v1/interview-links/vacancy/{vacancy_id}/stats",
            headers=hr_user["headers"]
        )
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_links"] == 1
        assert stats["used_links"] == 1
        assert stats["active_links"] == 0  # Link is used, so not active
        
        print(f"✅ Step 11: HR checked interview statistics")
        
        # Step 12: HR views all vacancies
        response = client.get(
            "/api/v1/vacancies/",
            headers=hr_user["headers"]
        )
        assert response.status_code == 200
        vacancies = response.json()
        assert vacancies["total"] == 1
        assert vacancies["vacancies"][0]["interview_links_count"] == 1
        
        print(f"✅ Step 12: HR viewed all vacancies")
        
        # Step 13: HR views interview links for the vacancy
        response = client.get(
            f"/api/v1/interview-links/?vacancy_id={vacancy_id}",
            headers=hr_user["headers"]
        )
        assert response.status_code == 200
        links = response.json()
        assert links["total"] == 1
        assert links["links"][0]["is_used"] == True
        assert links["links"][0]["candidate_name"] == "John Doe"
        
        print(f"✅ Step 13: HR viewed interview links")
        
        print("\n🎉 Complete workflow test passed successfully!")
        print("All steps from vacancy creation to interview completion worked correctly.")
    
    def test_error_scenarios(self, client, hr_user):
        """Test error scenarios in the workflow"""
        
        # Test 1: Try to access non-existent interview link
        response = client.get("/api/v1/candidate/access/invalid_token")
        assert response.status_code == 404
        
        # Test 2: Try to create interview link for non-existent vacancy
        link_data = {
            "candidate_name": "Test User",
            "candidate_email": "test@example.com",
            "expires_hours": 6
        }
        
        response = client.post(
            "/api/v1/interview-links/?vacancy_id=99999",
            json=link_data,
            headers=hr_user["headers"]
        )
        assert response.status_code == 404
        
        # Test 3: Try to access interview link without proper authentication
        response = client.get("/api/v1/interview-links/", headers={})
        assert response.status_code == 401
        
        print("✅ Error scenarios test passed")
    
    def test_link_expiration(self, client, hr_user):
        """Test interview link expiration"""
        
        # Create a vacancy
        vacancy_data = {
            "title": "Test Position",
            "description": "Test description",
            "company_name": "Test Company"
        }
        
        response = client.post(
            "/api/v1/vacancies/",
            json=vacancy_data,
            headers=hr_user["headers"]
        )
        vacancy_id = response.json()["id"]
        
        # Create an interview link with very short expiration (1 hour)
        link_data = {
            "candidate_name": "Test User",
            "candidate_email": "test@example.com",
            "expires_hours": 1
        }
        
        response = client.post(
            f"/api/v1/interview-links/?vacancy_id={vacancy_id}",
            json=link_data,
            headers=hr_user["headers"]
        )
        link_token = response.json()["unique_token"]
        
        # Mock the current time to be after expiration
        with patch('app.api.v1.candidate_access.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime.utcnow() + timedelta(hours=2)
            
            # Try to access expired link
            response = client.get(f"/api/v1/candidate/access/{link_token}")
            assert response.status_code == 200  # Link info is returned
            access_info = response.json()
            assert access_info["is_expired"] == True
            
            # Try to register with expired link
            candidate_data = {
                "candidate_name": "Test User",
                "candidate_email": "test@example.com"
            }
            
            response = client.post(
                f"/api/v1/candidate/access/{link_token}/register",
                json=candidate_data
            )
            assert response.status_code == 400
            assert "expired" in response.json()["detail"].lower()
        
        print("✅ Link expiration test passed")
    
    def test_file_upload_validation(self, client, hr_user):
        """Test file upload validation"""
        
        # Create a vacancy
        vacancy_data = {
            "title": "Test Position",
            "description": "Test description"
        }
        
        response = client.post(
            "/api/v1/vacancies/",
            json=vacancy_data,
            headers=hr_user["headers"]
        )
        vacancy_id = response.json()["id"]
        
        # Test uploading invalid file type
        with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as f:
            f.write("This is not a valid document")
            invalid_file = f.name
        
        try:
            with open(invalid_file, 'rb') as f:
                files = {"file": ("malware.exe", f, "application/octet-stream")}
                response = client.post(
                    f"/api/v1/vacancies/{vacancy_id}/upload-document",
                    files=files,
                    headers=hr_user["headers"]
                )
                assert response.status_code == 400
                assert "not supported" in response.json()["detail"]
                
        finally:
            if os.path.exists(invalid_file):
                os.unlink(invalid_file)
        
        print("✅ File upload validation test passed")


def run_tests():
    """Run all tests"""
    print("🚀 Starting comprehensive workflow tests...")
    print("=" * 60)
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")


if __name__ == "__main__":
    run_tests()
