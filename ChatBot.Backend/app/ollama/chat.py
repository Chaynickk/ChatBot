import aiohttp
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def get_ollama_response(prompt: str, model_name: str = "mistral"):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                OLLAMA_API_URL,
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {
                        "stop": ["User:", "Assistant:"]
                    }
                }
            ) as resp:
                while True:
                    line = await resp.content.readline()
                    if not line:
                        break
                    try:
                        # Отправляем строку как есть (один JSON-объект на строку)
                        yield line.decode("utf-8").rstrip("\r\n") + "\n"
                    except Exception as e:
                        yield json.dumps({"response": f"[Ошибка парсинга: {str(e)}]"}) + "\n"
    except Exception as e:
        yield json.dumps({"response": f"[Ошибка запроса: {str(e)}]"}) + "\n" 