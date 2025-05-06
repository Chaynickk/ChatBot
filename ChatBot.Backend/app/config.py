from pydantic import BaseSettings

class Settings(BaseSettings):
    ADMIN_TELEGRAM_ID: int

    class Config:
        env_file = ".env"

settings = Settings()
