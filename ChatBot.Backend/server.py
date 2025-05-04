import os
import time
import json
import subprocess
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Путь к фронтенду
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../ChatBot.Frontend"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

# Переменные окружения
API_KEY = os.getenv("API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")
API_GIGACHAT = os.getenv("API_GIGACHAT")
GEN_API = os.getenv("GEN_API")
RQUID = os.getenv("RQUID")

YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
GIGA_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
GEN_API_URL = "https://api.gen-api.ru/api/v1/networks/gpt-4o-mini"

PUBLIC_URL = "https://example.loca.lt"
access_token = None
token_expires_at = 0
latest_gpt4omini_responses = []

def get_access_token():
    global access_token, token_expires_at
    if access_token and time.time() < token_expires_at:
        return access_token

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {API_GIGACHAT}",
        "RqUID": RQUID
    }
    data = {"scope": "GIGACHAT_API_PERS"}
    try:
        r = requests.post(TOKEN_URL, data=data, headers=headers, verify=False, timeout=10)
        r.raise_for_status()
        access_token = r.json()["access_token"]
        token_expires_at = time.time() + 1800
        return access_token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения токена: {str(e)}")

@app.get("/chat/stream")
async def chat_stream(message: str):
    if not message:
        return StreamingResponse(content=iter(["data: [Пустое сообщение]\n\n"]), media_type="text/event-stream")

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
        "x-folder-id": FOLDER_ID,
        "Content-Type": "application/json"
    }
    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "completionOptions": {
            "stream": True,
            "temperature": 0.6,
            "maxTokens": 500
        },
        "messages": [
            {"role": "system", "text": "Ты дружелюбный ассистент. Рассказывай шутки"},
            {"role": "user", "text": message}
        ]
    }

    def event_stream():
        try:
            r = requests.post(YANDEX_API_URL, headers=headers, json=payload, stream=True)
            for line in r.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        text = chunk["result"]["alternatives"][0]["message"]["text"]
                        yield f"data: {text}\n\n"
                    except Exception as e:
                        yield f"data: [Ошибка парсинга: {str(e)}]\n\n"
        except Exception as e:
            yield f"data: [Ошибка запроса: {str(e)}]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/gigachat")
async def gigachat_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": "Ты дружелюбный ассистент"},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        r = requests.post(GIGA_API_URL, headers=headers, json=payload, timeout=15, verify=False)
        r.raise_for_status()
        return JSONResponse({"response": r.json()["choices"][0]["message"]["content"]})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GigaChat не отвечает: {str(e)}")

@app.post("/gpt4omini")
async def gpt4omini_chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="Пустое сообщение")

    headers = {
        "Authorization": f"Bearer {GEN_API}",
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": message}]
        }],
        "callback_url": f"{PUBLIC_URL}/gpt4omini_callback",
        "response_format": {"type": "text"},
        "is_sync": False
    }

    try:
        r = requests.post(GEN_API_URL, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        return JSONResponse({"status": "processing"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка общения с GPT-4o mini: {str(e)}")

@app.post("/gpt4omini_callback")
async def gpt4o_callback(request: Request):
    try:
        data = await request.json()
        message = data.get("result", [{}])[0].get("message", {}).get("content", "Ответ не получен.")
        latest_gpt4omini_responses.append(message)
        return JSONResponse({"status": "ok"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка в callback: {str(e)}")

@app.get("/gpt4omini_result")
async def get_gpt4o_result():
    if latest_gpt4omini_responses:
        return JSONResponse({"response": latest_gpt4omini_responses.pop(0)})
    return JSONResponse({"response": "Ответ не получен."})

def run_localtunnel():
    global PUBLIC_URL
    print("⏳ Запускаем LocalTunnel...")
    lt_path = os.path.expanduser(r"~\AppData\Roaming\npm\lt.cmd")
    proc = subprocess.Popen([lt_path, "--port", "5000"], stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        if "your url is:" in line:
            PUBLIC_URL = line.split("your url is:")[-1].strip()
            print(f"🌐 Публичный callback_url: {PUBLIC_URL}/gpt4omini_callback")
            break

if __name__ == "__main__":
    run_localtunnel()
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
