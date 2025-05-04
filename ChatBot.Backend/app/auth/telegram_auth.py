import hashlib
import hmac
import base64
import os
from typing import Dict

SECRET_KEY = os.getenv("TELEGRAM_BOT_TOKEN")  # Токен вашего бота из переменных окружения


def check_telegram_auth(init_data: str) -> Dict:
    """Проверяет подпись и возвращает данные пользователя"""

    # Получаем signature и сам init_data
    data, signature = init_data.split(":")

    # Создаем проверочную строку
    secret = SECRET_KEY.encode('utf-8')
    expected_signature = hmac.new(secret, data.encode('utf-8'), hashlib.sha256).digest()

    # Сравниваем их
    if base64.urlsafe_b64encode(expected_signature).decode('utf-8') == signature:
        # Если подпись верна, декодируем init_data в JSON
        user_data = base64.urlsafe_b64decode(data).decode('utf-8')
        return user_data  # Вернем данные о пользователе
    else:
        raise ValueError("Invalid signature")

