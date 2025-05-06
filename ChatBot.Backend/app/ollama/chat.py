import requests
from typing import AsyncGenerator, List, Dict
import json

OLLAMA_API_URL = "http://localhost:11434/api/chat"

async def get_ollama_response(messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
    """
    Получает ответ от Ollama по чанкам.
    
    Args:
        messages: Список сообщений для контекста
        
    Yields:
        str: Чанки ответа от модели
    """
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "messages": messages,
                "stream": True,
                "max_token": 1
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
                except Exception as e:
                    yield f"[Ошибка парсинга: {str(e)}]"
                    
    except Exception as e:
        yield f"[Ошибка запроса: {str(e)}]" 