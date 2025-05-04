import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.telegram_auth import verify_telegram_token
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_create_chat():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Предполагаем, что проект с ID 1 и модель с ID 1 уже существуют
        chat_data = {
            "user_id": 0,            # Telegram ID пользователя (зарегистрирован заранее)
            "title": "Test Chat",    # Название чата
            "model_id": 1            # ID модели
        }

        response = await ac.post("/api/chats/", json=chat_data)

        assert response.status_code == 200, response.text
        data = response.json()

        assert data["title"] == "Test Chat"
        assert data["user_id"] == 0
        assert "created_at" in data

