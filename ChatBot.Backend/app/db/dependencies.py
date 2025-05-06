from .database import AsyncSessionLocal
from typing import AsyncGenerator

async def get_async_session() -> AsyncGenerator:
    async with AsyncSessionLocal() as session:
        yield session
