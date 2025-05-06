from pydantic import BaseModel
from datetime import datetime

class FolderCreate(BaseModel):
    project_id: int
    name: str

class FolderOut(BaseModel):
    id: int
    project_id: int
    name: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
