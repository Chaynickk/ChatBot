from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_session
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
from fastapi import HTTPException
import traceback

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        print("📥 Регистрируем:", user)
        result = await create_user(db, user)
        print("✅ Успешно:", result)
        return result
    except Exception as e:
        print("❌ Ошибка при регистрации:")
        traceback.print_exc()  # <--- покажет, в чём ошибка
        raise HTTPException(status_code=500, detail="Ошибка на сервере: " + str(e))
