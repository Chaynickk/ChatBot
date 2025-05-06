from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from app.db.dependencies import get_async_session
from app.models.project import Project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.patch("/system-prompt")
async def update_project_system_prompt(
    project_id: int,
    telegram_id: int,
    system_prompt: str,
    db: AsyncSession = Depends(get_async_session)
):
    # Проверяем существование проекта и его принадлежность пользователю
    project_query = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == telegram_id
        )
    )
    project = project_query.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Проект не найден или не принадлежит указанному пользователю"
        )
    
    # Обновляем системный промпт
    await db.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(system_prompt=system_prompt)
    )
    await db.commit()
    
    return {"message": "Системный промпт проекта успешно обновлен"} 