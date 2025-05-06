import requests
from typing import AsyncGenerator, List, Dict
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def get_ollama_response(prompt: str) -> AsyncGenerator[str, None]:
    """
    Получает ответ от Ollama по чанкам.
    
    Args:
        prompt: Строка с промптом для модели
        
    Yields:
        str: Чанки ответа от модели
    """
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": True,
                "options": {
                    "stop": ["User:", "Assistant:"]
                }
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        yield chunk["response"]
                except Exception as e:
                    yield f"[Ошибка парсинга: {str(e)}]"
                    
    except Exception as e:
        yield f"[Ошибка запроса: {str(e)}]" 