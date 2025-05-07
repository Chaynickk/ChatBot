from pydantic import BaseModel

class UserCreate(BaseModel):
    telegram_id: int
    username: str
    full_name: str
    is_plus: bool
    custom_prompt: str | None = None

class UserOut(BaseModel):
    telegram_id: int
    username: str
    full_name: str
    is_plus: bool
    custom_prompt: str | None = None

    class Config:
        orm_mode = True


