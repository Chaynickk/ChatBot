from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.message import Message
from app.schemas.message import MessageCreate
from typing import List, Optional

async def create_message(db: AsyncSession, message: MessageCreate) -> Message:
    db_message = Message(**message.model_dump())
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def get_chat_messages(
    db: AsyncSession, 
    chat_id: int,
    before_id: Optional[int] = None,
    limit: int = 35
) -> List[Message]:
    query = select(Message).where(Message.chat_id == chat_id)
    
    if before_id:
        query = query.where(Message.id < before_id)
    
    query = query.order_by(Message.id.desc())
    if limit:
        query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    return result.scalar_one_or_none()
