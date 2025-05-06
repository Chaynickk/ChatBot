from fastapi.testclient import TestClient
from app.ollama.test import app

client = TestClient(app)

def test_empty_messages():
    response = client.post("/chat/stream", json={"model": "mistral", "messages": []})
    assert response.status_code == 200
    assert "[Пустое сообщение]" in response.content.decode("utf-8")


def test_prompt_generation():
    from app.ollama.test import messages_to_prompt
    messages = [
        {"role": "system", "content": "Ты философ."},
        {"role": "user", "content": "Что такое сознание?"}
    ]
    prompt = messages_to_prompt(messages)
    assert "Ты философ" in prompt
    assert "User: Что такое сознание?" in prompt
    assert prompt.endswith("Assistant:")


def test_stream_response():
    response = client.post("/chat/stream", json={
        "model": "mistral",
        "messages": [
            {"role": "system", "content": "Ты помощник."},
            {"role": "user", "content": "Привет!"}
        ]
    })

    content = response.content.decode("utf-8")
    full_answer = "".join([
        line.removeprefix("data: ").strip()
        for line in content.splitlines()
        if line.startswith("data: ")
    ])

    print("💬 Полный ответ модели:")
    print(full_answer)



def test_messages_to_prompt_memory_and_instructions():
    messages = [
        {"role": "system", "content": "Ты ИИ-ассистент."},
        {"role": "system", "content": "Память: пользователь учит Python."},
        {"role": "user", "content": "Как создать функцию?"},
    ]
    from app.ollama.test import messages_to_prompt
    prompt = messages_to_prompt(messages)
    assert "[ИНСТРУКЦИЯ]" in prompt
    assert "Память: пользователь учит Python" in prompt
    assert "User: Как создать функцию?" in prompt
