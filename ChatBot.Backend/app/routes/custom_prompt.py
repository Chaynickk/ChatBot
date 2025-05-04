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
    result = await db.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(custom_prompt=prompt)
        .execution_options(synchronize_session="fetch")
    )
    await db.commit()
    return {"message": "Промпт успешно обновлён"}
