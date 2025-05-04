from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.chat import ChatCreate, ChatOut
from app.crud.chat import create_chat, get_chat_by_id
from app.crud.user import get_user_by_telegram_id
from app.auth.telegram_auth import verify_telegram_token
from app.schemas.auth import TelegramAuth
from app.auth.security import api_key_header
import traceback
from typing import List
from sqlalchemy import select
from app.models.chat import Chat

router = APIRouter(prefix="/api", tags=["chats"])

@router.post("/chats/", response_model=ChatOut)
async def register_chat(chat: ChatCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        result = await create_chat(db, chat)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании чата: {str(e)}")

@router.get("/chats/", response_model=List[ChatOut])
async def get_chats(
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    auth_telegram_id: int = Depends(verify_telegram_token),
    db: AsyncSession = Depends(get_async_session),
    api_key: str = Security(api_key_header)
):
    """
    Получает чаты пользователя.

    Args:
        telegram_id: Telegram ID пользователя
        auth_telegram_id: Telegram ID из заголовка авторизации
        db: Сессия базы данных
        api_key: ключ авторизации (для Swagger UI)

    Returns:
        List[ChatOut]: Список чатов пользователя

    Raises:
        HTTPException: Если пользователь не авторизован или не найден
    """
    # Проверяем, что пользователь авторизован и запрашивает свои чаты
    if auth_telegram_id != telegram_id:
        raise HTTPException(
            status_code=403,
            detail="Нельзя получать чаты других пользователей"
        )

    # Проверяем существование пользователя
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Пользователь не найден"
        )

    # Получаем чаты пользователя
    query = select(Chat).where(Chat.user_id == telegram_id)

    # Сортируем по дате создания (новые сверху)
    query = query.order_by(Chat.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()
