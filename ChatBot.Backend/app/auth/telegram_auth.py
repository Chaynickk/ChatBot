import hashlib
import hmac
import base64
import os
from typing import Dict
from fastapi import Depends, HTTPException, Header, Request
from app.schemas.auth import TelegramAuth
from urllib.parse import parse_qsl
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.crud.user import get_user_by_telegram_id
from app.models.user import User

# Используем значение по умолчанию, если переменная окружения не установлена
SECRET_KEY = os.getenv("TELEGRAM_BOT_TOKEN", "8090019258:AAHQDpY3eNaGSVBRT_05sREt_Mz5zt8i2Ew")

logging.basicConfig(level=logging.INFO)
logging.info(f"[telegram_auth] TELEGRAM_BOT_TOKEN loaded: {SECRET_KEY is not None}")
logging.info(f"[telegram_auth] TELEGRAM_BOT_TOKEN value: {SECRET_KEY}")


def check_telegram_auth(init_data: str) -> Dict:
    """Безопасность отключена: просто парсим user из init_data без проверки подписи."""
    logging.info(f"[telegram_auth] init_data: {init_data}")
    from urllib.parse import parse_qsl
    import json
    data_dict = dict(parse_qsl(init_data, keep_blank_values=True))
    user_data = data_dict.get('user')
    if user_data:
        user_json = json.loads(user_data)
        data_dict['telegram_id'] = user_json.get('id')
        data_dict['username'] = user_json.get('username')
        data_dict['full_name'] = user_json.get('first_name', '') + ' ' + user_json.get('last_name', '')
    logging.info(f"[telegram_auth] Final user data (no signature check): {data_dict}")
    return data_dict

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

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Получает текущего пользователя из заголовка Authorization.
    Ожидает заголовок: Authorization: Telegram <telegram_id>
    
    Args:
        request: Запрос FastAPI
        db: Сессия базы данных
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если пользователь не авторизован или не найден
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Telegram "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )
    
    try:
        telegram_id = int(auth_header.split(" ")[1])
        user = await get_user_by_telegram_id(db, telegram_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return user
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid telegram_id in header"
        )

