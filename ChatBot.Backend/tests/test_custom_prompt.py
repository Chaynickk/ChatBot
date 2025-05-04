import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import insert
from app.main import app
from app.db.database import AsyncSessionLocal
from app.models.user import User

@pytest.mark.asyncio
async def test_update_custom_prompt():
    async with AsyncSessionLocal() as session:
        stmt = insert(User).values(
            telegram_id=1234596,
            username="test_user",
            full_name="Test User",
            is_plus=True
        )
        await session.execute(stmt)
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put("/users/prompt", params={
            "telegram_id": 1234596,
            "prompt": "This is a custom prompt"
        })

    assert response.status_code == 200
    assert response.json()["message"] == "Промпт успешно обновлён"
