from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import Chat
from app.schemas.chat import ChatCreate
from typing import Optional

async def create_chat(db: AsyncSession, chat: ChatCreate):
    new_chat = Chat(**chat.model_dump())
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat

async def get_chat_by_id(db: AsyncSession, chat_id: int) -> Optional[Chat]:
    """
    Получает чат по его ID.
    
    Args:
        db: Сессия базы данных
        chat_id: ID чата
        
    Returns:
        Optional[Chat]: Найденный чат или None, если чат не найден
    """
    result = await db.execute(
        select(Chat).where(Chat.id == chat_id)
    )
    return result.scalar_one_or_none()
