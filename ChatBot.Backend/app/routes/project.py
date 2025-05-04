from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.project import ProjectCreate, ProjectOut
from app.crud.project import create_project
from app.db.dependencies import get_async_session
from fastapi import APIRouter, Depends, Query, HTTPException
from app.models.project import Project
from sqlalchemy import select

router = APIRouter()

@router.post("/projects/", response_model=ProjectOut)
async def register_project(project: ProjectCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        return await create_project(db, project)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при создании проекта: {e}")

@router.get("/", response_model=list[ProjectOut])
async def get_projects(
    telegram_id: int = Query(...),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Project).where(Project.user_id == telegram_id)
    )
    return result.scalars().all()