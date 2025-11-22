from datetime import datetime

import httpx
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.domain.port.candlePort import ICandlePort
from app.infrastructure.models.candleTable import CandleTable


class CandleRepository(ICandlePort):

    def __init__(self, db: Session):
        self.db = db

    async def saveCandles(self, symbol: str, candles: list):
        stmt = insert(CandleTable).values([
            {
                "symbol": symbol,
                "open_time": c["open_time"],
                "open": c["open"],
                "high": c["high"],
                "low": c["low"],
                "close": c["close"]
            } for c in candles
        ]).on_conflict_do_nothing(
            index_elements=['symbol', 'open_time']  # ta clé unique
        )

        self.db.execute(stmt)
        self.db.commit()
        print(f"Ajout de {len(candles)} bougies pour {symbol}")
        print(f"Total bougies dans la table : {self.db.query(CandleTable).count()}")

    def deleteOlderThan(self, symbol: str, date: datetime):
        stmt = (
            delete(CandleTable)
            .where(CandleTable.symbol == symbol)
            .where(CandleTable.open_time < date)
        )

        self.db.execute(stmt)
        self.db.commit()

    def getCandlesBySymbol(self, symbol: str):
        rows = (
            self.db.query(CandleTable)
            .filter(CandleTable.symbol == symbol)
            .all()
        )
        return rows