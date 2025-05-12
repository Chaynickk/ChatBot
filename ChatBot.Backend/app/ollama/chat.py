import aiohttp
import json
import logging

OLLAMA_API_URL = "http://localhost:11434/api/generate"

async def get_ollama_response(prompt: str, model_name: str = "mistral"):
    logger = logging.getLogger(__name__)
    logger.info(f"[get_ollama_response] Вызвана с prompt: {prompt}, model_name: {model_name}")
    try:
        async with aiohttp.ClientSession() as session:
            logger.info(f"[get_ollama_response] Отправка POST {OLLAMA_API_URL}")
            async with session.post(
                OLLAMA_API_URL,
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": True
                }
            ) as resp:
                logger.info(f"[get_ollama_response] Статус ответа: {resp.status}")
                while True:
                    line = await resp.content.readline()
                    logger.info(f"[get_ollama_response] readline: {line}")
                    if not line:
                        logger.info(f"[get_ollama_response] Чтение завершено (пустая строка)")
                        break
                    try:
                        decoded = line.decode("utf-8").rstrip("\r\n") + "\n"
                        logger.info(f"[get_ollama_response] chunk: {decoded}")
                        yield decoded
                    except Exception as e:
                        logger.error(f"[get_ollama_response] Ошибка парсинга: {e}")
                        yield json.dumps({"response": f"[Ошибка парсинга: {str(e)}]"}) + "\n"
    except Exception as e:
        logger.error(f"[get_ollama_response] Ошибка запроса: {e}")
        yield json.dumps({"response": f"[Ошибка запроса: {str(e)}]"}) + "\n" 