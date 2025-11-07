import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check if required activities exist
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    """Test successful activity signup"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Chess Club" in response.json()["message"]
    
    # Verify the student was actually added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test signing up a student who is already registered"""
    # First signup
    client.post(
        "/activities/Programming Class/signup",
        params={"email": "teststudent@mergington.edu"}
    )
    
    # Try to signup again
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": "teststudent@mergington.edu"}
    )
    assert response.status_code == 400
    assert "Student already signed up for this activity" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for an activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]