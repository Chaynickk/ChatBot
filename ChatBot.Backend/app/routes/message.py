from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.message import MessageCreate, MessageOut
from app.crud.message import create_message, get_chat_messages, get_message_by_id
from app.crud.chat import get_chat_by_id
from app.ollama.chat import get_ollama_response
from typing import List, Optional
from fastapi.responses import StreamingResponse
import json
from datetime import datetime

router = APIRouter(prefix="/messages", tags=["messages"])

def serialize_message(message: MessageOut) -> dict:
    """Преобразует сообщение в словарь с сериализованным datetime"""
    data = message.dict()
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

@router.post("/messages/")
async def send_message(
    message: MessageCreate,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # Получаем чат, чтобы узнать его parent_message_id
        chat = await get_chat_by_id(db, message.chat_id)
        if not chat:
            raise HTTPException(
                status_code=404,
                detail=f"Chat {message.chat_id} not found"
            )
        
        # Создаем сообщение пользователя с parent_id из чата
        user_message = await create_message(db, MessageCreate(
            chat_id=message.chat_id,
            content=message.content,
            role="user",
            parent_id=chat.parent_message_id
        ))
        user_message_out = MessageOut.from_orm(user_message)
        
        # Получаем историю сообщений для контекста
        chat_messages = await get_chat_messages(db, chat_id=message.chat_id, limit=10)
        
        # Формируем сообщения для Ollama
        messages_for_ollama = [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in reversed(chat_messages)  # Переворачиваем, чтобы старые сообщения были первыми
        ]
        
        # Добавляем системное сообщение
        messages_for_ollama.insert(0, {
            "role": "system",
            "content": "Ты дружелюбный ассистент. Отвечай кратко и по делу."
        })
        
        async def event_stream():
            # Отправляем сообщение пользователя
            yield f"data: {json.dumps({'type': 'user_message', 'data': serialize_message(user_message_out)})}\n\n"
            
            # Создаем сообщение ассистента с тем же parent_id
            assistant_message = MessageCreate(
                chat_id=message.chat_id,
                content="",
                role="assistant",
                parent_id=chat.parent_message_id
            )
            assistant_message_db = await create_message(db, assistant_message)
            assistant_message_out = MessageOut.from_orm(assistant_message_db)
            
            # Получаем и отправляем ответ от Ollama по чанкам
            full_response = ""
            async for chunk in get_ollama_response(messages_for_ollama):
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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )

@router.get("/messages/", response_model=List[MessageOut])
async def get_messages(
    chat_id: int,
    limit: int = Query(default=50, le=100),
    before_id: Optional[int] = None,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        messages = await get_chat_messages(
            db,
            chat_id=chat_id,
            limit=limit,
            before_id=before_id
        )
        return [MessageOut.from_orm(msg) for msg in messages]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages: {str(e)}"
        )
