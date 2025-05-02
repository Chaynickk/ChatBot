from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json


app = FastAPI()

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat/stream")
async def ollama_stream(request: Request):
    body = await request.json()
    model = body.get("model", "mistral")
    messages = body.get("messages", [])

    if not messages:
        return StreamingResponse(iter(["data: [Пустое сообщение]\n\n"]), media_type="text/event-stream")
    print(messages)
    prompt = messages_to_prompt(messages=messages)

    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "stop": ["User:", "Assistant:"]
        }
    }

    url = "http://localhost:11434/api/generate"

    def event_stream():
        try:
            with requests.post(url, json=data, stream=True) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            text = chunk.get("response", "")
                            yield f"data: {text}\n\n"
                        except Exception as e:
                            yield f"data: [Ошибка парсинга: {str(e)}]\n\n"
        except Exception as e:
            yield f"data: [Ошибка запроса: {str(e)}]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

def messages_to_prompt(messages: list[dict]) -> str:
    role_format = {
        "system": "[ИНСТРУКЦИЯ]\n{content}\n\n",
        "user": "User: {content}\n",
        "assistant": "Assistant: {content}\n"
    }

    prompt = ""
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "").strip()
        if role in role_format:
            prompt += role_format[role].format(content=content)
    prompt += "Assistant:"  # чтобы модель продолжила
    return prompt



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ollama.test:app", host="0.0.0.0", port=8000, reload=True)
