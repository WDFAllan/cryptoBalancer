from app.infrastructure.repository.candle.baseCandleRepository import BaseCandleRepository

from app.infrastructure.models.candle.candleTreeMTable import CandleThreeMTable



class threeMinCandleRepository(BaseCandleRepository):

    def __init__(self, db):
        super().__init__(db, CandleThreeMTable)

    def getCandlesBySymbol(self, symbol: str):
        rows = (
            self.db.query(CandleThreeMTable)
            .filter(CandleThreeMTable.symbol == symbol)
            .all()
        )
        return rows
