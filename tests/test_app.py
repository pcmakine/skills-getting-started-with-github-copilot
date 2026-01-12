"""Tests for the Mergington High School Activities API"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Basketball": {
            "description": "Team sport focusing on basketball skills and competitive play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis techniques and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums and create masterpieces",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu", "alex@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in plays and musicals, develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking through debates",
            "schedule": "Mondays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["aisha@mergington.edu", "jacob@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["ryan@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for getting activities"""

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Basketball" in data
        assert "Programming Class" in data

    def test_get_activities_contains_correct_structure(self, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for signing up for activities"""

    def test_signup_new_student(self, reset_activities):
        """Test that a new student can sign up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_student(self, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, reset_activities):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_full_activity(self, reset_activities):
        """Test signup for activity that might be full"""
        # Fill up Basketball (max 15 participants)
        for i in range(14):
            activities["Basketball"]["participants"].append(f"student{i}@mergington.edu")
        
        # Try to add one more (should succeed as it's at 15 max)
        response = client.post(
            "/activities/Basketball/signup?email=overstudent@mergington.edu"
        )
        assert response.status_code == 200


class TestUnregister:
    """Tests for unregistering from activities"""

    def test_unregister_existing_student(self, reset_activities):
        """Test that a student can unregister from an activity"""
        # Verify student is signed up
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_student(self, reset_activities):
        """Test that unregister fails for student not in activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test that unregister fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_then_signup_again(self, reset_activities):
        """Test that a student can sign up again after unregistering"""
        student_email = "michael@mergington.edu"
        
        # Unregister
        response = client.post(
            f"/activities/Chess Club/unregister?email={student_email}"
        )
        assert response.status_code == 200
        assert student_email not in activities["Chess Club"]["participants"]
        
        # Sign up again
        response = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert response.status_code == 200
        assert student_email in activities["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests"""

    def test_signup_and_verify_in_list(self, reset_activities):
        """Test that signed up student appears in activity list"""
        email = "testintegration@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Programming Class/signup?email={email}")
        
        # Verify in list
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]

    def test_full_user_journey(self, reset_activities):
        """Test complete user journey: signup, view, unregister"""
        email = "journey@mergington.edu"
        activity = "Drama Club"
        
        # 1. Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # 2. Get activities and verify
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # 3. Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # 4. Verify removal
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
