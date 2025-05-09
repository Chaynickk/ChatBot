import requests
import time

URL = "https://33e13f42b6e346.lhr.life/api/projects/?telegram_id=0"  # замени на свой публичный URL, если нужно

while True:
    try:
        response = requests.get(URL)
        print(f"Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Ошибка запроса: {e}")
    time.sleep(10)