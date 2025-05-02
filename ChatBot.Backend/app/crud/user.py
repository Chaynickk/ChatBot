from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    stmt = select(User).where(User.telegram_id == user_data.telegram_id)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return existing_user  # не создаём дубликат

    new_user = User(**user_data.dict())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
