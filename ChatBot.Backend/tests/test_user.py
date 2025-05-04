from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/users/",
        json={
            "telegram_id": 123456789,
            "username": "testuser",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["telegram_id"] == 123456789
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "created_at" in data
