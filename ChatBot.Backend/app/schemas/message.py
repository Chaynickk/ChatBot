from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    chat_id: int
    content: str
    role: str = "user"  # может быть 'user', 'assistant' или 'system'
    parent_id: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True

class MessageOut(BaseModel):
    id: int
    chat_id: int
    content: str
    role: str
    parent_id: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
