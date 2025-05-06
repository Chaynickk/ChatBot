from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.db.dependencies import get_async_session
from app.models.chat import Chat
from app.models.folder import Folder

router = APIRouter(prefix="/chats", tags=["chats"])

@router.patch("/settings")
async def update_chat_settings(
    chat_id: int,
    telegram_id: int,
    project_id: int | None = None,
    folder_id: int | None = None,
    db: AsyncSession = Depends(get_async_session)
):
    # Проверяем существование чата и его принадлежность пользователю
    chat_query = await db.execute(
        select(Chat).where(
            Chat.id == chat_id,
            Chat.user_id == telegram_id
        )
    )
    chat = chat_query.scalar_one_or_none()
    
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Чат не найден или не принадлежит указанному пользователю"
        )
    
    # Если указан folder_id, проверяем его принадлежность к project_id
    if folder_id is not None:
        # Определяем project_id для проверки (либо новый, либо текущий из чата)
        check_project_id = project_id if project_id is not None else chat.project_id
        
        if check_project_id is None:
            raise HTTPException(
                status_code=400,
                detail="Нельзя назначить папку без указания проекта"
            )
            
        # Проверяем существование папки и её принадлежность к проекту
        folder_query = await db.execute(
            select(Folder).where(
                Folder.id == folder_id,
                Folder.project_id == check_project_id
            )
        )
        folder = folder_query.scalar_one_or_none()
        
        if not folder:
            raise HTTPException(
                status_code=404,
                detail="Папка не найдена или не принадлежит указанному проекту"
            )
    
    # Обновляем настройки чата
    update_data = {}
    if project_id is not None:
        update_data["project_id"] = project_id
        # Если меняется проект, сбрасываем папку
        update_data["folder_id"] = None
    if folder_id is not None:
        update_data["folder_id"] = folder_id
    
    if update_data:
        await db.execute(
            update(Chat)
            .where(Chat.id == chat_id)
            .values(**update_data)
        )
        await db.commit()
    
    return {"message": "Настройки чата успешно обновлены"} 