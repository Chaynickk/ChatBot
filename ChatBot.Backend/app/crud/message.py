from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.schemas.message import MessageCreate

async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
    new_message = Message(**message.model_dump())
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message
