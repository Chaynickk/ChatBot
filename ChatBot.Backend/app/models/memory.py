from sqlalchemy import Column, Integer, BigInteger, Text, TIMESTAMP
from datetime import datetime, timezone
from app.db.database import Base

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
