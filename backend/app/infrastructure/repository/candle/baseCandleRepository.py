from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.domain.port.candlePort import ICandlePort


class BaseCandleRepository(ICandlePort):

    def __init__(self, db: Session,table):
        self.db = db
        self.table = table

    async def saveCandles(self, symbol: str, candles: list):
        stmt = insert(self.table).values([
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
        print(f"Total bougies dans la table : {self.db.query(self.table).count()}")