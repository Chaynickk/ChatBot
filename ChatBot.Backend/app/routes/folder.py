from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.folder import FolderCreate, FolderOut
from app.crud.folder import create_folder
from app.models.project import Project
from app.models.folder import Folder

router = APIRouter(prefix="/folders", tags=["folders"])

@router.post("/folders/", response_model=FolderOut)
async def register_folder(folder: FolderCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        return await create_folder(db, folder)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании папки: {str(e)}")

@router.patch("/{folder_id}/rename")
async def rename_folder(folder_id: int, new_name: str, telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    # Получаем папку
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Папка не найдена")
    # Получаем проект
    project = await db.get(Project, folder.project_id)
    if not project or project.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Нет доступа к этой папке")
    # Переименовываем
    folder.name = new_name
    await db.commit()
    await db.refresh(folder)
    return folder
