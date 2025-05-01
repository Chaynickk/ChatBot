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

@app.get("/chat/stream")
async def ollama_stream(message: str, model: str = "mistral"):
    if not message:
        return StreamingResponse(iter(["data: [Пустое сообщение]\n\n"]), media_type="text/event-stream")

    url = "http://localhost:11434/api/generate"
    # data = {
    #   "model": "mistral",
    #   "prompt": "Объясни, как работает нейросеть.",
    #   "system": "Ты — преподаватель по ИИ. Отвечай кратко, понятно, с примерами, избегая жаргона.",
    #   "template": "default",
    #   "context": [101, 202, 303],
    #   "images": [
    #     "iVBORw0KGgoAAAANSUhEUgAA..."
    #   ],
    #   "stream": true,
    #   "format": "json",
    #   "raw": false,
    #   "options": {
    #     "temperature": 0.7,
    #     "top_p": 0.9,
    #     "top_k": 40,
    #     "repeat_penalty": 1.1,
    #     "presence_penalty": 0.3,
    #     "frequency_penalty": 0.3,
    #     "stop": ["User:", "Assistant:"],
    #     "seed": 42,
    #     "num_predict": 300
    #   }
    # }
    prompt = build_prompt(system="",question=message, project="", memory="", history="")
    data = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "stop": ["User:", "Assistant:"]
    }



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

def build_prompt(system, project, memory, history, question):
    return f"""
[ИНСТРУКЦИЯ]
{system}

[ПРОЕКТ]
{project}

[ПАМЯТЬ]
{memory}

[ЧАТ]
{history}
User: {question}
Assistant:"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ollama.test:app", host="0.0.0.0", port=8000, reload=True)
