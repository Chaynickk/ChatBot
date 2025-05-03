import pytest
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from app.main import app
from app.db.dependencies import get_async_session

@pytest.mark.asyncio
async def test_create_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        new_message = {
            "chat_id": 3,
            "role": "user",
            "content": "Hello from test!",
            "parent_id": None
        }

        response = await ac.post("/messages/", json=new_message)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["chat_id"] == 2
        assert data["role"] == "user"
        assert data["content"] == "Hello from test!"
