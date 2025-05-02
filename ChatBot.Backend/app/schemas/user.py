from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserOut(BaseModel):
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    is_plus: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

