from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime, timezone

from app.core.database.database import Base


class PortfolioValueTable(Base):
    __tablename__ = "portfolio_value"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    totalValue = Column(Float, nullable=False)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc))

