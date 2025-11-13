from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database.database import Base


class WalletItemTable(Base):
    __tablename__ = "walletItem"

    id = Column(Integer, primary_key=True, autoincrement=True)
    walletId = Column(Integer, ForeignKey("wallet.id"), nullable=False)
    symbol = Column(String, nullable=False)
    amount = Column(Float, default=0.0)

    wallet = relationship("WalletTable", back_populates="items")