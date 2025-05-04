from pydantic import BaseModel

class UserCreate(BaseModel):
    telegram_id: int
    username: str
    full_name: str
    is_plus: bool

class UserOut(BaseModel):
    telegram_id: int
    username: str
    full_name: str
    is_plus: bool

    class Config:
        orm_mode = True


