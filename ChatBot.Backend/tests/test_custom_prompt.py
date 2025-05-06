import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.user import User

@pytest.mark.asyncio
async def test_update_custom_prompt_existing_user():
    telegram_id = 0  # Используйте telegram_id реально существующего пользователя в вашей БД

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            "/users/prompt",
            params={"telegram_id": telegram_id, "prompt": "Новый промпт"}
        )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Промпт успешно обновлён"

    # Проверяем, что custom_prompt реально обновился в БД
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        assert user.custom_prompt == "Новый промпт"