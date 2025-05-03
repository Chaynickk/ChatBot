from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.db.dependencies import get_async_session
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.put("/prompt")
async def update_custom_prompt(
    telegram_id: int,
    prompt: str,
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.custom_prompt = prompt
    await db.commit()
    return {"message": "Промпт успешно обновлён"}
