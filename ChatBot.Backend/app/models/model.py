from sqlalchemy import Column, Integer, String, Boolean
from app.models.user import Base

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    provider = Column(String, nullable=False)
    is_public = Column(Boolean, default=True)
