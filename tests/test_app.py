"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities_returns_200(self):
        """Test that getting activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that activities response is a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_basketball(self):
        """Test that activities include Basketball"""
        response = client.get("/activities")
        data = response.json()
        assert "Basketball" in data
    
    def test_basketball_has_required_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        basketball = data["Basketball"]
        
        assert "description" in basketball
        assert "schedule" in basketball
        assert "max_participants" in basketball
        assert "participants" in basketball
    
    def test_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_data["participants"], list)


class TestSignUp:
    """Tests for signing up for activities"""
    
    def test_signup_with_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_invalid_activity(self):
        """Test signing up for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_signup_duplicate_participant(self):
        """Test that duplicate signup returns 400"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_adds_participant_to_list(self):
        """Test that signup actually adds participant to activity"""
        email = "verify@mergington.edu"
        
        # Signup
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Get activities and verify participant is there
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregister@mergington.edu"
        
        # Sign up first
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Unregister
        response = client.post(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "unregistered" in data["message"].lower()
    
    def test_unregister_invalid_activity(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_non_participant(self):
        """Test unregistering a non-participant returns 400"""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_removes_participant(self):
        """Test that unregister actually removes participant"""
        email = "remove@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Verify signed up
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Verify removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball"]["participants"]


class TestRoot:
    """Tests for root endpoint"""
    
    def test_root_redirects(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
