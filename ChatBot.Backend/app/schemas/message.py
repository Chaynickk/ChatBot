from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    chat_id: int
    parent_id: Optional[int] = None
    role: str
    content: str

class MessageOut(MessageCreate):
    id: int
    created_at: datetime
