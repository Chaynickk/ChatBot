from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.schemas.project import ProjectCreate

async def create_project(db: AsyncSession, project: ProjectCreate) -> Project:
    new_project = Project(**project.model_dump())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    return new_project
