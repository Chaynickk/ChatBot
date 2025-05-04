from pydantic import BaseModel

class ModelCreate(BaseModel):
    name: str
    provider: str
    is_public: bool = True

class ModelOut(BaseModel):
    id: int
    name: str
    provider: str
    is_public: bool

    model_config = {
        "from_attributes": True
    }
