from fastapi.testclient import TestClient
from app.main import app

def test_get_chats_sync():
    client = TestClient(app)
    telegram_id = 0  # Используйте telegram_id существующего пользователя
    response = client.get(
        f"/api/chats/?telegram_id={telegram_id}",
        headers={"Authorization": f"Telegram {telegram_id}"}
    )
    assert response.status_code in (200, 404), response.text
    if response.status_code == 200:
        data = response.json()
        print(data)
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "user_id" in data[0]
            assert "title" in data[0] 