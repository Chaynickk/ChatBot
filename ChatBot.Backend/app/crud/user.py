from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Optional

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        is_plus=user.is_plus
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    """
    Получает пользователя по его Telegram ID.
    
    Args:
        db: Сессия базы данных
        telegram_id: Telegram ID пользователя
        
    Returns:
        Optional[User]: Найденный пользователь или None, если пользователь не найден
    """
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()
