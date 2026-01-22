import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
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
        },
        "Basketball": {
            "description": "Team basketball games and skills training",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis lessons and competitive matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore physics, chemistry, and biology through experiments",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_includes_participants(self, client, reset_activities):
        """Test that activities include participant list"""
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant_to_activity(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client, reset_activities):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_for_activity_already_signed_up_fails(self, client, reset_activities):
        """Test signup fails if student already signed up"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_with_empty_email_passes(self, client, reset_activities):
        """Test signup with empty email (API currently accepts it)"""
        # Note: This test documents current behavior. In production, you may want
        # to add email validation to reject empty strings
        response = client.post("/activities/Chess%20Club/signup?email=")
        # Currently the API accepts empty email, this documents that behavior
        assert response.status_code == 200


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_participant_success(self, client, reset_activities):
        """Test successful unregistration of a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Participant unregistered successfully" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test unregister for non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonExistent%20Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test unregister for non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess%20Club/participants/nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
