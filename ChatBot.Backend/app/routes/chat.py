from fastapi import APIRouter, Depends, HTTPException, Query, Security
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.chat import ChatCreate, ChatOut, ChatRename
from app.crud.chat import create_chat, get_chat_by_id
from app.crud.user import get_user_by_telegram_id
from app.auth.telegram_auth import verify_telegram_token
from app.schemas.auth import TelegramAuth
from app.auth.security import api_key_header
from app.schemas.message import MessageCreate, MessageOut
from app.crud.message import create_message
from app.ollama.chat import get_ollama_response
from app.ollama.prompt import get_chat_prompt
import traceback
from typing import List
from sqlalchemy import select
from app.models.chat import Chat
from fastapi.responses import StreamingResponse
import json
from datetime import datetime

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

@router.patch("/chats/{chat_id}/rename", response_model=ChatOut)
async def rename_chat(
    chat_id: int,
    rename_data: ChatRename,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        chat = await get_chat_by_id(db, chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Чат не найден")
        
        if chat.user_id != rename_data.telegram_id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому чату")
        
        chat.title = rename_data.new_title
        await db.commit()
        await db.refresh(chat)
        return chat
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при переименовании чата: {str(e)}")

@router.post("/chats/branch/", response_model=ChatOut)
async def create_chat_branch(
    parent_chat_id: int,
    parent_message_id: int,
    user_message: str,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # Получаем родительский чат
        parent_chat = await get_chat_by_id(db, parent_chat_id)
        if not parent_chat:
            raise HTTPException(status_code=404, detail="Родительский чат не найден")

        # Создаем новый чат
        new_chat = ChatCreate(
            user_id=parent_chat.user_id,
            project_id=parent_chat.project_id,
            folder_id=parent_chat.folder_id,
            model_id=parent_chat.model_id,
            parent_chat_id=parent_chat_id,
            parent_message_id=parent_message_id,
            title=f"Ветка от чата {parent_chat_id}"
        )
        
        # Сохраняем новый чат
        chat = await create_chat(db, new_chat)
        
        # Создаем первое сообщение в новом чате
        user_message_db = await create_message(db, MessageCreate(
            chat_id=chat.id,
            content=user_message,
            role="user",
            parent_id=parent_message_id
        ))
        user_message_out = MessageOut.from_orm(user_message_db)

        # Получаем полный контекст чата и преобразуем его в промпт
        prompt = await get_chat_prompt(db, chat.user_id, chat.id)

        async def event_stream():
            # Отправляем сообщение пользователя
            yield f"data: {json.dumps({'type': 'user_message', 'data': serialize_message(user_message_out)})}\n\n"
            
            # Создаем сообщение ассистента
            assistant_message = MessageCreate(
                chat_id=chat.id,
                content="",
                role="assistant",
                parent_id=parent_message_id
            )
            assistant_message_db = await create_message(db, assistant_message)
            assistant_message_out = MessageOut.from_orm(assistant_message_db)
            
            # Получаем и отправляем ответ от Ollama по чанкам
            full_response = ""
            async for chunk in get_ollama_response(prompt):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk})}\n\n"
            
            # Обновляем сообщение ассистента полным ответом
            assistant_message_db.content = full_response
            await db.commit()
            await db.refresh(assistant_message_db)
            assistant_message_out = MessageOut.from_orm(assistant_message_db)
            
            # Отправляем финальное сообщение ассистента
            yield f"data: {json.dumps({'type': 'assistant_message', 'data': serialize_message(assistant_message_out)})}\n\n"
        
        return StreamingResponse(event_stream(), media_type="text/event-stream")
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании ветки чата: {str(e)}")

def serialize_message(message: MessageOut) -> dict:
    """Преобразует сообщение в словарь с сериализованным datetime"""
    data = message.dict()
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data
