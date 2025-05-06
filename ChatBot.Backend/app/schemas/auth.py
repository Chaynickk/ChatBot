from pydantic import BaseModel, Field

class TelegramAuth(BaseModel):
    """
    Схема для данных авторизации Telegram.
    
    Attributes:
        id: Telegram ID пользователя
        first_name: Имя пользователя
        last_name: Фамилия пользователя (опционально)
        username: Имя пользователя в Telegram (опционально)
        photo_url: URL фотографии пользователя (опционально)
        auth_date: Время авторизации
        hash: Хеш для проверки подписи
        init_data: Исходные данные авторизации
    """
    id: int = Field(..., description="Telegram ID пользователя")
    first_name: str = Field(..., description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")
    username: str | None = Field(None, description="Имя пользователя в Telegram")
    photo_url: str | None = Field(None, description="URL фотографии пользователя")
    auth_date: int = Field(..., description="Время авторизации")
    hash: str = Field(..., description="Хеш для проверки подписи")
    init_data: str = Field(..., description="Исходные данные авторизации") 