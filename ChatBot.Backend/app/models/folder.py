from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, TIMESTAMP
from datetime import datetime, UTC
from app.db.database import Base

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(UTC))
