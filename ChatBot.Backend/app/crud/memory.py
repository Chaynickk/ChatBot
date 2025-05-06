from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.memory import Memory
from typing import List

async def get_memories_by_telegram_id(db: AsyncSession, telegram_id: int) -> List[Memory]:
    """
    Получает последние 10 воспоминаний пользователя по его Telegram ID.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        
    Returns:
        List[Memory]: Список из 10 последних воспоминаний пользователя, отсортированный по дате создания (новые сверху)
    """
    query = select(Memory).where(Memory.user_id == telegram_id).order_by(Memory.created_at.desc()).limit(10)
    result = await db.execute(query)
    return result.scalars().all() 