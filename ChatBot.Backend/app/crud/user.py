from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, exists, delete
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Optional
from datetime import datetime, timedelta
from app.models.subscription import Subscription

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

async def update_all_users_is_plus(db: AsyncSession):
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    # Обновить is_plus = True для пользователей с активной подпиской
    await db.execute(
        update(User)
        .values(is_plus=True)
        .where(
            exists().where(
                (Subscription.user_id == User.telegram_id) &
                (Subscription.started_at > thirty_days_ago) &
                (Subscription.status == 'active')
            )
        )
    )
    # Обновить is_plus = False для остальных
    await db.execute(
        update(User)
        .values(is_plus=False)
        .where(~exists().where(
            (Subscription.user_id == User.telegram_id) &
            (Subscription.started_at > thirty_days_ago) &
            (Subscription.status == 'active')
        ))
    )
    await db.commit()

async def delete_expired_subscriptions(db: AsyncSession):
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    await db.execute(
        delete(Subscription)
        .where(
            (Subscription.started_at <= thirty_days_ago) |
            (Subscription.status != 'active')
        )
    )
    await db.commit()
