from pydantic import BaseModel
from datetime import datetime

class MemoryCreate(BaseModel):
    user_id: int
    content: str

class MemoryOut(MemoryCreate):
    id: int
    created_at: datetime
    model_config = {
        "from_attributes": True
    }
