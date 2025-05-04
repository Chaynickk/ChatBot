import hashlib
import hmac
import base64
import os
from typing import Dict
from fastapi import Depends, HTTPException, Header
from app.schemas.auth import TelegramAuth

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

async def verify_telegram_auth(auth: TelegramAuth) -> TelegramAuth:
    """
    Проверяет авторизацию пользователя через Telegram.
    
    Args:
        auth: Данные авторизации Telegram
        
    Returns:
        TelegramAuth: Проверенные данные авторизации
        
    Raises:
        HTTPException: Если авторизация не прошла
    """
    try:
        # Проверяем подпись
        check_telegram_auth(auth.init_data)
        return auth
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Неверная авторизация Telegram"
        )

async def verify_telegram_token(authorization: str = Header(..., alias="Authorization")) -> int:
    """
    Проверяет токен авторизации Telegram.
    Ожидает заголовок: Authorization: Telegram <telegram_id>
    """
    if not authorization.startswith("Telegram "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    try:
        telegram_id = int(authorization.split(" ")[1])
        return telegram_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid telegram_id in header")

