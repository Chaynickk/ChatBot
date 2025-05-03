from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session as get_db
from app.schemas.message import MessageCreate, MessageOut
from app.crud.message import create_message

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageOut)
async def create_message_route(
    message: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_message(db, message)
