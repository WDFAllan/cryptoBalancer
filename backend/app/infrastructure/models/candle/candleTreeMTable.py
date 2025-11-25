from sqlalchemy import UniqueConstraint, Column, Float, DateTime, String, Integer

from app.core.database.database import Base


class CandleThreeMTable(Base):
    __tablename__ = 'candleThreeMin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    open_time = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    __table_args__ = (
        UniqueConstraint("symbol", "open_time", name="uq_symbol_time_3min_candle"),
    )