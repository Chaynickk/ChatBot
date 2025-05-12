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

    if not init_data or ':' not in init_data:
        raise ValueError("Invalid init_data format: missing separator")

    # Получаем signature и сам init_data
    try:
        data, signature = init_data.split(":")
    except ValueError:
        raise ValueError("Invalid init_data format: incorrect separator usage")

    if not SECRET_KEY:
        raise ValueError("TELEGRAM_BOT_TOKEN not configured")

    # Создаем проверочную строку
    try:
        secret = SECRET_KEY.encode('utf-8')
        expected_signature = hmac.new(secret, data.encode('utf-8'), hashlib.sha256).digest()
    except Exception as e:
        raise ValueError(f"Error creating signature: {str(e)}")

    # Сравниваем их
    try:
        if base64.urlsafe_b64encode(expected_signature).decode('utf-8') == signature:
            # Если подпись верна, декодируем init_data в JSON
            user_data = base64.urlsafe_b64decode(data).decode('utf-8')
            return user_data  # Вернем данные о пользователе
        else:
            raise ValueError("Invalid signature")
    except Exception as e:
        raise ValueError(f"Error verifying signature: {str(e)}")

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

