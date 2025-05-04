from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session as get_db
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryOut

router = APIRouter(prefix="/memories", tags=["memories"])

@router.post("/", response_model=MemoryOut)
async def create_memory(
    memory: MemoryCreate,
    db: AsyncSession = Depends(get_db)
):
    new_memory = Memory(**memory.model_dump())
    db.add(new_memory)
    await db.commit()
    await db.refresh(new_memory)
    return new_memory
