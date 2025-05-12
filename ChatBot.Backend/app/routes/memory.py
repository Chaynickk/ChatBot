from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session as get_db
from app.models.memory import Memory
from app.schemas.memory import MemoryCreate, MemoryOut, MemoryUpdate

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

@router.put("/{memory_id}", response_model=MemoryOut)
async def update_memory(
    memory_id: int,
    memory_update: MemoryUpdate,
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):
    memory = await db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    if memory.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this memory")
    
    memory.content = memory_update.content
    await db.commit()
    await db.refresh(memory)
    return memory
