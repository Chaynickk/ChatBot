from sqlalchemy.ext.asyncio import AsyncSession
from app.models.folder import Folder
from app.schemas.folder import FolderCreate

async def create_folder(db: AsyncSession, folder: FolderCreate):
    new_folder = Folder(**folder.model_dump())
    db.add(new_folder)
    await db.commit()
    await db.refresh(new_folder)
    return new_folder
