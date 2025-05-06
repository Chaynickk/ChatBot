from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.message import Message
from app.models.chat import Chat
from app.models.project import Project
from app.crud.memory import get_memories_by_telegram_id

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

async def get_chat_context(db: AsyncSession, telegram_id: int, chat_id: int) -> List[Dict[str, str]]:
    """
    Получает полный контекст чата, включая долговременную память, историю сообщений и системный промпт проекта.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        chat_id: ID чата
        
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
    
    # Получаем последние 50 сообщений чата
    messages_query = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    )
    chat_messages = messages_query.scalars().all()
    
    # Добавляем сообщения в обратном порядке (от старых к новым)
    for msg in reversed(chat_messages):
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    return messages

async def get_chat_prompt(db: AsyncSession, telegram_id: int, chat_id: int) -> str:
    """
    Получает полный контекст чата и преобразует его в промпт для модели.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        chat_id: ID чата
        
    Returns:
        str: Отформатированный промпт для модели, включающий долговременную память,
             системный промпт проекта и историю сообщений
    """
    messages = await get_chat_context(db, telegram_id, chat_id)
    return messages_to_prompt(messages) 