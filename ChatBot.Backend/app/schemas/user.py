from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    is_plus: bool = False
    created_at: Optional[datetime] = None
    custom_prompt: Optional[str] = None

class UserOut(UserCreate):
    pass

    class Config:
        orm_mode = True


