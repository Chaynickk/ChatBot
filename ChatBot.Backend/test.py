import requests
from server import get_access_token

def print_gigachat_models(token):
    try:
        url = "https://gigachat.devices.sberbank.ru/api/v1/models"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        models = response.json()
        print("🧠 Доступные модели GigaChat:")
        for model in models.get("data", []):
            print(f" - {model.get('id')} | {model.get('object')}")
    except Exception as e:
        print("❌ Ошибка при получении списка моделей GigaChat:", e)

if __name__ == "__main__":
    token = get_access_token()
    print_gigachat_models(token)
