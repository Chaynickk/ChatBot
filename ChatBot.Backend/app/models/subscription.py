from sqlalchemy import Column, Integer, BigInteger, TIMESTAMP, String, ForeignKey
from app.db.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id", ondelete="CASCADE"), nullable=False)
    started_at = Column(TIMESTAMP, nullable=False)
    ended_at = Column(TIMESTAMP, nullable=True)
    status = Column(String, nullable=False) 