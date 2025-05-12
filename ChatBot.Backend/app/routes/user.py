from fastapi import APIRouter, HTTPException, Depends
from app.auth.telegram_auth import check_telegram_auth
from app.schemas.user import UserCreate, UserOut
from app.crud.user import create_user, get_user_by_telegram_id, update_all_users_is_plus, delete_expired_subscriptions
from app.db.dependencies import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subscription import Subscription
from sqlalchemy import select, update, delete
from datetime import datetime, timezone, timedelta
from app.models.user import User
import logging

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/users/", response_model=UserOut)
async def register_user(init_data: str, db: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"[register_user] Получен init_data: {init_data}")
        user_data = check_telegram_auth(init_data)  # Проверка данных Telegram
        logging.info(f"[register_user] После check_telegram_auth: {user_data}")
        user = UserCreate(**user_data)
        result = await create_user(db, user)
        logging.info(f"[register_user] Пользователь создан: {result}")
        return result
    except HTTPException as e:
        logging.error(f"[register_user] HTTPException: {e.detail}")
        raise
    except Exception as e:
        logging.error(f"[register_user] Ошибка: {e}")
        raise HTTPException(status_code=400, detail="Ошибка регистрации: " + str(e))

@router.get("/users/")
async def get_user(init_data: str, db: AsyncSession = Depends(get_async_session)):
    try:
        logging.info(f"[get_user] Получен init_data: {init_data}")
        user_data = check_telegram_auth(init_data)
        logging.info(f"[get_user] После check_telegram_auth: {user_data}")
        user = await get_user_by_telegram_id(db, user_data["telegram_id"])
        if not user:
            logging.warning(f"[get_user] User not found: {user_data['telegram_id']}")
            raise HTTPException(status_code=404, detail="User not found")
        logging.info(f"[get_user] Пользователь найден: {user}")
        return user
    except HTTPException as e:
        logging.error(f"[get_user] HTTPException: {e.detail}")
        raise
    except Exception as e:
        logging.error(f"[get_user] Ошибка: {e}")
        raise HTTPException(status_code=400, detail="Ошибка получения пользователя: " + str(e))

@router.post("/users/sync_plus_status")
async def sync_plus_status(db: AsyncSession = Depends(get_async_session)):
    try:
        now = datetime.utcnow()
        # 1. Обновить статус на expired для подписок, у которых истёк срок
        await db.execute(
            update(Subscription)
            .where((Subscription.ended_at <= now) & (Subscription.status == 'active'))
            .values(status='expired')
        )
        await db.commit()
        # 2. Обновить поле is_plus у пользователей
        await update_all_users_is_plus(db)
        return {"detail": "Plus-статусы синхронизированы: подписки обновлены, is_plus обновлён"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка синхронизации plus-статусов: " + str(e))

@router.post("/users/give_plus")
async def give_plus(telegram_id: int, db: AsyncSession = Depends(get_async_session)):
    try:
        now = datetime.utcnow()  # offset-naive
        thirty_days_ago = now - timedelta(days=30)
        # Проверяем, есть ли уже активная и неистёкшая подписка
        result = await db.execute(
            select(Subscription).where(
                (Subscription.user_id == telegram_id) &
                (Subscription.status == 'active') &
                (Subscription.started_at > thirty_days_ago)
            )
        )
        active_sub = result.scalar_one_or_none()
        if active_sub:
            raise HTTPException(status_code=400, detail="У пользователя уже есть активная подписка")
        # Создаем новую подписку с ended_at через 30 дней
        ended_at = now + timedelta(days=30)
        new_sub = Subscription(
            user_id=telegram_id,
            started_at=now,
            ended_at=ended_at,
            status='active'
        )
        db.add(new_sub)
        # Обновляем статус пользователя
        await db.execute(
            update(User).where(User.telegram_id == telegram_id).values(is_plus=True)
        )
        await db.commit()
        await db.refresh(new_sub)
        return {"detail": "Плюс подписка выдана", "subscription_id": new_sub.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Ошибка выдачи подписки: " + str(e))
