from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    system_prompt = Column(Text, nullable=True)

    # Связь с пользователем
    user = relationship("User", backref="projects")
