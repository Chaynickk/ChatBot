from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.message import MessageCreate, MessageOut
from app.crud.message import create_message, get_chat_messages, get_message_by_id
from app.crud.chat import get_chat_by_id
from app.ollama.chat import get_ollama_response
from app.ollama.prompt import get_chat_prompt, extract_text_from_file
from typing import List, Optional
from fastapi.responses import StreamingResponse
import json
from datetime import datetime
from sqlalchemy import select
from app.models.chat import Chat
from app.models.model import Model
from app.models.user import User
import traceback
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from app.auth.telegram_auth import get_current_user
from app.models.message import Message

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/messages", tags=["messages"])

def serialize_message(message: MessageOut) -> dict:
    """Преобразует сообщение в словарь с сериализованным datetime"""
    data = message.dict()
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

@router.post("/")
async def send_message(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    import json
    body_raw = await request.body()
    if not body_raw:
        logger.error("[send_message] Empty request body")
        raise HTTPException(status_code=400, detail="Empty request body")
        return
    try:
        body = json.loads(body_raw.decode("utf-8"))
    except Exception as e:
        logger.error(f"[send_message] Error parsing JSON: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or empty JSON")
        return
    logger.debug(f"[send_message] Request body: {body}")
    
    # Извлекаем параметры из JSON
    chat_id = body.get('chat_id')
    content = body.get('content')
    parent_id = body.get('parent_id')
    files = body.get('files', [])
    
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id is required")
        return
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
        return
        
    # Проверяем существование чата
    chat_query = await db.execute(select(Chat).filter(Chat.id == chat_id))
    chat = chat_query.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
        return
    if chat.user_id != current_user.telegram_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this chat")
        return
    # Сохраняем сообщение пользователя
    user_message = Message(
        chat_id=chat_id,
        content=content,
        parent_id=parent_id if parent_id else None,
        role="user"
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)
    logger.debug(f"[send_message] Created user message: {user_message.id}")

    prompt = await get_chat_prompt(db, current_user.telegram_id, chat_id, parent_id)
    model_name = "mistral"

    async def event_stream():
        full_response = ""
        # Стримим чанки Ollama
        async for chunk in get_ollama_response(prompt, model_name):
            try:
                data = json.loads(chunk)
                if "response" in data:
                    full_response += data["response"]
                yield chunk  # Отправляем чанк во фронт
            except Exception:
                continue
        # После стрима сохраняем сообщение ассистента
        assistant_message = Message(
            chat_id=chat_id,
            content=full_response,
            parent_id=user_message.id,
            role="assistant"
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)
        logger.debug(f"[send_message] Created assistant message: {assistant_message.id}")

    return StreamingResponse(event_stream(), media_type="text/plain")

@router.get("/", response_model=List[MessageOut])
async def get_messages(
    chat_id: int,
    before_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = []
        current_chat_id = chat_id
        current_before_id = before_id
        while current_chat_id:
            messages = await get_chat_messages(
                db,
                chat_id=current_chat_id,
                before_id=current_before_id
            )
            if not messages:
                break
            # Добавляем в начало, чтобы порядок был от старых к новым
            result = messages[::-1] + result
            # Если не хватает — ищем parent_id первого сообщения
            first_msg = messages[0]
            parent_id = getattr(first_msg, "parent_id", None)
            if not parent_id:
                break
            parent_msg = await get_message_by_id(db, parent_id)
            if not parent_msg:
                break
            current_chat_id = parent_msg.chat_id
            current_before_id = parent_msg.id
        return [MessageOut.from_orm(msg) for msg in result]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages: {str(e)}"
        )

@router.get("/in_chat/", response_model=List[MessageOut])
async def get_messages_in_chat(
    chat_id: int,
    before_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        messages = await get_chat_messages(
            db,
            chat_id=chat_id,
            before_id=before_id
        )
        return [MessageOut.from_orm(msg) for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages in chat: {str(e)}"
        )
