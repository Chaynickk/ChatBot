from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project import ProjectCreate, ProjectOut, ProjectRename
from app.crud.project import create_project
from app.db.dependencies import get_async_session
from fastapi import APIRouter, Depends, Query, HTTPException
from app.models.project import Project
from sqlalchemy import select
import logging
import traceback

router = APIRouter(prefix="/api", tags=["projects"])

@router.post("/projects/", response_model=ProjectOut)
async def register_project(project: ProjectCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"Попытка создать проект: {project}")
        new_project = await create_project(db, project)
        logging.info(f"Проект создан: {new_project}")
        return new_project
    except Exception as e:
        logging.error(f"Ошибка при создании проекта: {str(e)}")
        logging.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")

@router.get("/projects/", response_model=list[ProjectOut])
async def get_projects(
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Project).where(Project.user_id == telegram_id)
    )
    return result.scalars().all()

@router.patch("/projects/{project_id}/rename", response_model=ProjectOut)
async def rename_project(
    project_id: int,
    rename_data: ProjectRename,
    db: AsyncSession = Depends(get_async_session)
):
    try:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Проект не найден")
        
        if project.user_id != rename_data.telegram_id:
            raise HTTPException(status_code=403, detail="Нет доступа к этому проекту")
        
        project.name = rename_data.new_name
        await db.commit()
        await db.refresh(project)
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при переименовании проекта: {str(e)}")