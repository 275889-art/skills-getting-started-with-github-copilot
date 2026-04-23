from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    # Arrange
    url = "/"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success():
    # Arrange
    url = "/activities/Chess Club/signup?email=test1@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up test1@example.com for Chess Club" in result["message"]

    # Arrange
    verify_url = "/activities"

    # Act
    response2 = client.get(verify_url)

    # Assert
    assert "test1@example.com" in response2.json()["Chess Club"]["participants"]


def test_signup_duplicate():
    # Arrange
    signup_url = "/activities/Programming Class/signup?email=test2@example.com"
    client.post(signup_url)

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]


def test_signup_invalid_activity():
    # Arrange
    url = "/activities/Invalid Activity/signup?email=test3@example.com"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_unreg_success():
    # Arrange
    signup_url = "/activities/Gym Class/signup?email=test4@example.com"
    client.post(signup_url)

    # Act
    response = client.delete(signup_url)

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered test4@example.com from Gym Class" in result["message"]

    # Arrange
    verify_url = "/activities"

    # Act
    response2 = client.get(verify_url)

    # Assert
    assert "test4@example.com" not in response2.json()["Gym Class"]["participants"]


def test_unreg_not_signed():
    # Arrange
    url = "/activities/Chess Club/signup?email=notsigned@example.com"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]


def test_unreg_invalid_activity():
    # Arrange
    url = "/activities/Invalid Activity/signup?email=test5@example.com"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]