from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.folder import FolderCreate, FolderOut
from app.crud.folder import create_folder

router = APIRouter()

@router.post("/folders/", response_model=FolderOut)
async def register_folder(folder: FolderCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        return await create_folder(db, folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании папки: {str(e)}")
