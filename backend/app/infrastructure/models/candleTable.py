from sqlalchemy import Column, Integer, String, DateTime, Float, UniqueConstraint

from app.core.database.database import Base


class CandleTable(Base):
    __tablename__ = 'candle'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    open_time = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    __table_args__ = (
        UniqueConstraint("symbol", "open_time", name="uq_symbol_time"),
    )