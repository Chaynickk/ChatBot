import os
import subprocess
import threading
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
PUBLIC_URL = "https://example.loca.lt"  # ← сюда перед запуском нужно записать актуальный URL

@app.post("/gpt4omini_callback")
async def callback(request: Request):
    data = await request.json()
    print("📨 Получен callback от GPT-4o mini:")
    print(data)
    return JSONResponse(content={"status": "ok"})

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=4000)

def run_localtunnel():
    global PUBLIC_URL
    print("⏳ Запускаем LocalTunnel...")

    lt_path = os.path.expanduser(r"~\AppData\Roaming\npm\lt.cmd")
    proc = subprocess.Popen([lt_path, "--port", "5000"], stdout=subprocess.PIPE, text=True)

    for line in proc.stdout:
        if "your url is:" in line:
            public_url = line.split("your url is:")[-1].strip()
            PUBLIC_URL = public_url
            print(f"🌐 Публичный callback_url: {public_url}/gpt4omini_callback")
            break

if __name__ == "__main__":
    threading.Thread(target=run_fastapi).start()
    run_localtunnel()
