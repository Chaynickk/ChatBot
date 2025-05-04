import pytest
from httpx import AsyncClient
from fastapi import status
from httpx import ASGITransport
from app.main import app  # замените на путь к вашему FastAPI app

@pytest.mark.asyncio
async def test_create_memory():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        memory_data = {
            "user_id": 0,
            "content": "Воспоминание из теста"
        }

        response = await ac.post("/memories/", json=memory_data)
        assert response.status_code == status.HTTP_200_OK, response.text

        data = response.json()
        assert data["user_id"] == memory_data["user_id"]
        assert data["content"] == memory_data["content"]
        assert "id" in data
        assert "created_at" in data
