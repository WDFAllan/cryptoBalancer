from enum import Enum as PyEnum
from sqlalchemy import Column, Enum as SQLEnum
from datetime import datetime
from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database.database import Base

class TransactionType(PyEnum):
    ADD = "ADD"
    REMOVE = "REMOVE"
    UPDATE = "UPDATE"



class WalletTransactionTable(Base):
    __tablename__ = "wallet_transaction"

    id = Column(Integer, primary_key=True, autoincrement=True)

    walletId = Column(Integer, ForeignKey("wallet.id"), nullable=False)

    transactionType = Column(
        SQLEnum(TransactionType, name="transaction_type_enum"),
        nullable=False
    )

    symbol = Column(String(20), nullable=False)

    amount = Column(Float, nullable=False)
    previousAmount = Column(Float, nullable=True)

    reason = Column(String(50), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    wallet = relationship("WalletTable")
