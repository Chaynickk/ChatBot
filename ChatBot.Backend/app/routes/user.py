from fastapi import APIRouter, HTTPException, Depends
from app.auth.telegram_auth import check_telegram_auth
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user
import traceback
from app.db.dependencies import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/users/", response_model=UserOut)
async def register_user(init_data: str, db: AsyncSession = Depends(get_async_session)):
    try:
        user_data = check_telegram_auth(init_data)  # Проверка данных Telegram
        user = UserCreate(**user_data) 
        result = await create_user(db, user)
        return result
    except Exception as e:
        traceback.print_exc()  
        raise HTTPException(status_code=400, detail="Ошибка регистрации: " + str(e))
