import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture()
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Arrange — nothing; use initial state

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.headers.get("cache-control") == "no-store"
    data = response.json()
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Tennis Club",
        "Art Studio",
        "Drama Club",
        "Debate Team",
        "Science Club",
    ]
    for name in expected_activities:
        assert name in data


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={existing_email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    unknown_activity = "Unknown Activity"
    assert unknown_activity not in activities

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/participants
# ---------------------------------------------------------------------------

def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={existing_email}")

    # Assert
    assert response.status_code == 200
    assert "message" in response.json()
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_not_registered_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    unregistered_email = "notregistered@mergington.edu"
    assert unregistered_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={unregistered_email}")

    # Assert
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    unknown_activity = "Unknown Activity"
    assert unknown_activity not in activities

    # Act
    response = client.delete(f"/activities/{unknown_activity}/participants?email=student@mergington.edu")

    # Assert
    assert response.status_code == 404
