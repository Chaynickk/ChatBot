import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_project():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        project_data = {
            "name": "Test Project",
            "user_id": 0
        }
        response = await ac.post("/projects/", json=project_data)

        assert response.status_code == 200, response.text
        data = response.json()

        assert data["name"] == "Test Project"
        assert data["user_id"] == 0
        assert "created_at" in data
