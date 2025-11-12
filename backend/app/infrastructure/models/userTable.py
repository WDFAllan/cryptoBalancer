from sqlalchemy import Column, Integer, String
from app.core.database.database import Base

class UserTable(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True,index=True)
    email = Column(String,unique=True,index=True)
    username = Column(String)