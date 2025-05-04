from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.chat import Chat
from app.schemas.chat import ChatCreate

async def create_chat(db: AsyncSession, chat: ChatCreate):
    new_chat = Chat(**chat.model_dump())
    db.add(new_chat)
    await db.commit()
    await db.refresh(new_chat)
    return new_chat
