from app.routes import user, project, folder
from app.models.user import Base
from app.db.database import engine
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user.router)
app.include_router(project.router)
app.include_router(folder.router)

@app.get("/ping")
def ping():
    return {"message": "pong"}

