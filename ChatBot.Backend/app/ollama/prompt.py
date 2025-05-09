from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.message import Message
from app.models.chat import Chat
from app.models.project import Project
from app.crud.memory import get_memories_by_telegram_id
from app.crud.message import get_chat_messages

def messages_to_prompt(messages: List[Dict[str, str]]) -> str:
    """
    Преобразует список сообщений в форматированный промпт для модели.
    
    Args:
        messages: Список сообщений в формате [{"role": str, "content": str}, ...]
        
    Returns:
        str: Отформатированный промпт для модели
    """
    role_format = {
        "system": "[ИНСТРУКЦИЯ]\n{content}\n\n",
        "user": "User: {content}\n",
        "assistant": "Assistant: {content}\n"
    }

    prompt = ""
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "").strip()
        if role in role_format:
            prompt += role_format[role].format(content=content)
    prompt += "Assistant:"  # чтобы модель продолжила
    return prompt

async def get_chat_context(db: AsyncSession, telegram_id: int, chat_id: int, parent_message_id: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Получает полный контекст чата, включая долговременную память, историю сообщений и системный промпт проекта.
    Учитывает сообщения из родительских чатов для поддержания контекста ветвления.
    Если указан parent_message_id, добавляет сообщение, на которое отвечает пользователь.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        chat_id: ID чата
        parent_message_id: ID сообщения, на которое отвечает пользователь
        
    Returns:
        List[Dict[str, str]]: Список сообщений в формате [{"role": str, "content": str}, ...]
    """
    messages = []
    
    # Получаем долговременную память
    memories = await get_memories_by_telegram_id(db, telegram_id)
    if memories:
        memory_content = "\n".join([f"- {memory.content}" for memory in memories])
        messages.append({
            "role": "system",
            "content": f"Долговременная память пользователя:\n{memory_content}"
        })
    
    # Получаем чат и его проект
    chat_query = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    chat = chat_query.scalar_one_or_none()
    
    if chat and chat.project_id:
        # Получаем системный промпт проекта
        project_query = await db.execute(
            select(Project).where(Project.id == chat.project_id)
        )
        project = project_query.scalar_one_or_none()
        if project and project.system_prompt:
            messages.append({
                "role": "system",
                "content": project.system_prompt
            })
    
    # Если есть parent_message_id, получаем сообщение, на которое отвечает пользователь
    if parent_message_id:
        parent_message_query = await db.execute(
            select(Message).where(Message.id == parent_message_id)
        )
        parent_message = parent_message_query.scalar_one_or_none()
        if parent_message:
            messages.append({
                "role": "system",
                "content": f"Пользователь отвечает на сообщение ассистента:\n{parent_message.content}"
            })
    
    # Получаем сообщения с учетом родительских чатов
    chat_messages = await get_chat_messages(db, chat_id=chat_id, limit=50)
    
    # Добавляем сообщения в обратном порядке (от старых к новым)
    for msg in reversed(chat_messages):
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return messages

async def get_chat_prompt(db: AsyncSession, telegram_id: int, chat_id: int, parent_message_id: Optional[int] = None) -> str:
    """
    Получает полный контекст чата и преобразует его в промпт для модели.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        chat_id: ID чата
        parent_message_id: ID сообщения, на которое отвечает пользователь
        
    Returns:
        str: Отформатированный промпт для модели, включающий долговременную память,
             системный промпт проекта и историю сообщений
    """
    messages = await get_chat_context(db, telegram_id, chat_id, parent_message_id)
    return messages_to_prompt(messages)

import os
from io import BytesIO
from docx import Document
import pandas as pd
import pdfplumber
from fastapi import UploadFile

async def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename
    ext = os.path.splitext(filename)[-1].lower()
    content = await file.read()
    stream = BytesIO(content)

    try:
        if ext == ".docx":
            doc = Document(stream)
            return "\n".join([para.text for para in doc.paragraphs])

        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(stream)
            return df.to_csv(index=False)

        elif ext == ".csv":
            df = pd.read_csv(stream)
            return df.to_csv(index=False)

        elif ext == ".pdf":
            text = ""
            with pdfplumber.open(stream) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()

        elif ext == ".txt":
            return content.decode("utf-8")

        else:
            return f"[❌ Неподдерживаемый формат файла: {ext}]"

    except Exception as e:
        return f"[⚠️ Ошибка при обработке файла: {str(e)}]"
