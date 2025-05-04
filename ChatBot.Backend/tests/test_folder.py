import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_folder():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        folder_data = {
            "project_id": 2,  # или 0 — в зависимости от существующего проекта в БД
            "name": "Test Folder"
        }
        response = await ac.post("/folders/", json=folder_data)

        assert response.status_code == 200, response.text
        data = response.json()

        assert data["project_id"] == folder_data["project_id"]
        assert data["name"] == folder_data["name"]
        assert "created_at" in data
        assert "id" in data
