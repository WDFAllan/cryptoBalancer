from sqlalchemy import Column, Integer, String, DateTime, func
from app.core.database.database import Base

class UserTable(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True,index=True)
    email = Column(String,unique=True,index=True)
    username = Column(String)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())