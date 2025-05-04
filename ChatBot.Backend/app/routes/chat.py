from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.chat import ChatCreate, ChatOut
from app.crud.chat import create_chat
import traceback
from fastapi import Query

router = APIRouter()

@router.post("/chats/", response_model=ChatOut)
async def register_chat(chat: ChatCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        result = await create_chat(db, chat)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании чата: {str(e)}")

from sqlalchemy import select
from app.models.chat import Chat
from app.schemas.chat import ChatOut

@router.get("/", response_model=list[ChatOut])
async def get_chats(
    project_id: int = Query(...),
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Chat).where(
            Chat.project_id == project_id,
            Chat.user_id == telegram_id
        )
    )
    return result.scalars().all()
