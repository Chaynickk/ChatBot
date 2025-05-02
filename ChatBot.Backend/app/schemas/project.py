from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    user_id: int  # telegram_id

class ProjectOut(ProjectCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
