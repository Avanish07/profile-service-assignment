from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_and_read_profile():
    payload = {
        "user_id": "candidate-user-001",
        "full_name": "Candidate User",
        "email": "candidate-user-001@example.com",
        "role": "student",
    }
    create_response = client.post("/profiles", json=payload)
    assert create_response.status_code in (201, 409)

    read_response = client.get("/profiles/candidate-user-001")
    assert read_response.status_code == 200
    assert read_response.json()["user_id"] == payload["user_id"]


def test_profile_not_found():
    response = client.get("/profiles/does-not-exist")
    assert response.status_code == 404
