from sqlalchemy import Column, Integer, BigInteger, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"))
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="SET NULL"), nullable=True)
    title = Column(Text, nullable=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    parent_chat_id = Column(Integer, ForeignKey("chats.id", ondelete="SET NULL"), nullable=True)
    parent_message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
