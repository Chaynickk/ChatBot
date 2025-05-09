from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
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

router = APIRouter(prefix="/messages", tags=["messages"])

def serialize_message(message: MessageOut) -> dict:
    """Преобразует сообщение в словарь с сериализованным datetime"""
    data = message.dict()
    if isinstance(data.get('created_at'), datetime):
        data['created_at'] = data['created_at'].isoformat()
    return data

@router.post("/messages/")
async def send_message(
    chat_id: int = Form(...),
    content: str = Form(...),
    role: str = Form("user"),
    parent_id: Optional[int] = Form(None),
    files: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_async_session)
):
    try:
        # Проверяем количество файлов
        if files and len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed"
            )

        # Проверяем размер каждого файла
        for file in files or []:
            if file.size > 10 * 1024 * 1024:  # 10 MB
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds 10MB limit"
                )

        # Получаем чат, чтобы узнать его parent_message_id
        chat = await get_chat_by_id(db, chat_id)
        if not chat:
            raise HTTPException(
                status_code=404,
                detail=f"Chat {chat_id} not found"
            )
        
        # Если есть файлы, извлекаем из них текст
        file_contents = []
        if files:
            for file in files:
                try:
                    content_from_file = await extract_text_from_file(file)
                    if content_from_file.startswith("[❌") or content_from_file.startswith("[⚠️"):
                        raise HTTPException(
                            status_code=400,
                            detail=f"Error processing file {file.filename}: {content_from_file}"
                        )
                    file_contents.append(f"=== Текст из файла {file.filename} ===\n{content_from_file}")
                except Exception as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Error processing file {file.filename}: {str(e)}"
                    )
        
        # Создаем сообщение пользователя с parent_id из чата (НЕ передаём files)
        user_message = await create_message(db, MessageCreate(
            chat_id=chat_id,
            content=content,
            role=role,
            parent_id=parent_id
        ))
        user_message_out = MessageOut.from_orm(user_message)
        
        # Получаем полный контекст чата и преобразуем его в промпт
        prompt = await get_chat_prompt(db, chat.user_id, chat_id)
        
        # Если есть текст из файлов, добавляем его в промпт
        if file_contents:
            files_text = "\n\n".join(file_contents)
            prompt = f"Текст из загруженных файлов:\n{files_text}\n\n{prompt}"
        
        async def event_stream():
            # Отправляем сообщение пользователя
            yield f"data: {json.dumps({'type': 'user_message', 'data': serialize_message(user_message_out)})}\n\n"
            
            # Создаем сообщение ассистента с тем же parent_id
            assistant_message = MessageCreate(
                chat_id=chat_id,
                content="",
                role="assistant",
                parent_id=parent_id
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
        result = []
        current_chat_id = chat_id
        current_before_id = before_id
        while len(result) < limit and current_chat_id:
            messages = await get_chat_messages(
                db,
                chat_id=current_chat_id,
                limit=limit - len(result),
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
        return [MessageOut.from_orm(msg) for msg in result[-limit:]]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch messages: {str(e)}"
        )

@router.get("/messages/in_chat/", response_model=List[MessageOut])
async def get_messages_in_chat(
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
            detail=f"Failed to fetch messages in chat: {str(e)}"
        )
