from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
from sqlalchemy import text
import sys

# Настраиваем логирование для этого модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Добавляем вывод в консоль
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

from app.database.database import get_db
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message
from app.responses.message_response import MessageResponse
from app.utils.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.debug(f"=== Starting get_chat_messages ===")
    logger.debug(f"Parameters: chat_id={chat_id}, user_id={current_user.id}")
    
    # Проверяем существование чата
    try:
        # Сначала проверяем просто существование чата
        check_chat = db.execute(text("""
            SELECT id, user_id, title 
            FROM chats 
            WHERE id = :chat_id
        """), {"chat_id": chat_id}).fetchone()
        
        logger.debug(f"Chat existence check result: {check_chat}")
        
        if not check_chat:
            logger.error(f"Chat {chat_id} does not exist in database")
            # Показываем все чаты пользователя
            all_chats = db.execute(text("""
                SELECT id, title, user_id 
                FROM chats 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC
            """), {"user_id": current_user.id}).fetchall()
            logger.debug(f"All chats for user {current_user.id}: {all_chats}")
            raise HTTPException(status_code=404, detail="Chat not found")
            
        # Проверяем принадлежность чата пользователю
        if check_chat.user_id != current_user.id:
            logger.error(f"Chat {chat_id} exists but belongs to user {check_chat.user_id}, not {current_user.id}")
            raise HTTPException(status_code=403, detail="Not authorized to access this chat")
            
        logger.debug(f"Found chat: id={check_chat.id}, user_id={check_chat.user_id}, title={check_chat.title}")
        
        # Получаем сообщения
        messages = db.query(Message).filter(Message.chat_id == chat_id).all()
        logger.debug(f"Found {len(messages)} messages for chat {chat_id}")
        
        return messages
        
    except Exception as e:
        logger.error(f"Error in get_chat_messages: {str(e)}", exc_info=True)
        raise 