from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.db.dependencies import get_async_session as get_db
from app.models.chat import Chat
from app.models.project import Project
from app.models.folder import Folder
from app.models.memory import Memory

router = APIRouter(prefix="/delete", tags=["delete"])


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    chat = await db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    if chat.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.execute(delete(Chat).where(Chat.parent_chat_id == chat_id))
    await db.execute(delete(Chat).where(Chat.id == chat_id))
    await db.commit()
    return {"message": "Чат удалён"}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    project = await db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if project.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.execute(delete(Chat).where(Chat.project_id == project_id))
    await db.execute(delete(Folder).where(Folder.project_id == project_id))
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()
    return {"message": "Проект удалён"}

@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    folder = await db.get(Folder, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Папка не найдена")

    project = await db.get(Project, folder.project_id)
    if not project or project.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.execute(delete(Chat).where(Chat.folder_id == folder_id))
    await db.execute(delete(Folder).where(Folder.id == folder_id))
    await db.commit()
    return {"message": "Папка удалена"}

@router.delete("/memory/{memory_id}")
async def delete_memory(memory_id: int, telegram_id: int, db: AsyncSession = Depends(get_db)):
    memory = await db.get(Memory, memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    if memory.user_id != telegram_id:
        raise HTTPException(status_code=403, detail="Нет доступа")

    await db.delete(memory)
    await db.commit()
    return {"message": "Запись удалена"}
