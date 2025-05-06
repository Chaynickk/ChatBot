from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ChatCreate(BaseModel):
    user_id: int
    project_id: Optional[int] = None
    folder_id: Optional[int] = None
    title: Optional[str] = None
    model_id: Optional[int] = None
    parent_chat_id: Optional[int] = None
    parent_message_id: Optional[int] = None

class ChatOut(ChatCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatRename(BaseModel):
    new_title: str
    telegram_id: int
