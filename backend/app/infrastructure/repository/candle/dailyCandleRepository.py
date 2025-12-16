from datetime import datetime

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain.port.candlePort import ICandlePort
from app.infrastructure.models.candle import candleTable
from app.infrastructure.models.candle.candleTable import CandleTable
from app.infrastructure.repository.candle.baseCandleRepository import BaseCandleRepository


class dailyCandleRepository(BaseCandleRepository):

    def __init__(self, db):
        super().__init__(db, CandleTable)


    def deleteOlderThan(self, symbol: str, minDate: datetime):
        self.db.query(CandleTable).filter(
            CandleTable.symbol == symbol,
            CandleTable.open_time < minDate
        ).delete()
        self.db.commit()

    def getCandlesBySymbol(self, symbol: str):
        rows = (
            self.db.query(CandleTable)
            .filter(CandleTable.symbol == symbol)
            .all()
        )
        return rows

    def getAllCandles(self):
        rows = (
            self.db.query(CandleTable).all()
        )
        return rows