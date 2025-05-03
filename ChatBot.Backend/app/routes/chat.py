from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.chat import ChatCreate, ChatOut
from app.crud.chat import create_chat
import traceback

router = APIRouter()

@router.post("/chats/", response_model=ChatOut)
async def register_chat(chat: ChatCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        result = await create_chat(db, chat)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при создании чата: {str(e)}")
