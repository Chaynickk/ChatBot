from app.routes import user, project, folder, chat, message, memory, custom_prompt, delete
from app.models.user import Base
from app.db.database import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI, Security
from app.auth.security import api_key_header
from app.models.message import Message

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(folder.router)
app.include_router(chat.router)
app.include_router(message.router)
app.include_router(memory.router)
app.include_router(custom_prompt.router)
app.include_router(delete.router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

