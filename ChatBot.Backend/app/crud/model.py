from app.models.model import Model
from app.schemas.model import ModelCreate
from sqlalchemy.ext.asyncio import AsyncSession

async def create_model(db: AsyncSession, model: ModelCreate):
    new_model = Model(**model.model_dump())
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)
    return new_model
