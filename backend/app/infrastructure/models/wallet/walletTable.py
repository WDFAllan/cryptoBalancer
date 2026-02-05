from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database.database import Base


class WalletTable(Base):
    __tablename__ = "wallet"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, unique=True, nullable=False)
    strategy = Column(String, nullable=True)
    items = relationship("WalletItemTable", back_populates="wallet", cascade="all, delete-orphan")