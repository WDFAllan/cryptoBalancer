from app.domain.services.candle.baseCandleService import baseCandleService
from app.infrastructure.models.candle.candleThreeMTable import CandleThreeMTable


class threeMinutesCandleService(baseCandleService):
    def __init__(self, candleRepo, cryptoRepo, binanceAdapter):
        super().__init__(
            candleRepo,
            cryptoRepo,
            binanceAdapter,
            timeframe="3m",
            retention_days=30
        )

    def getCandlesBySymbol(self, symbol: str):
        return self.candleRepo.getCandlesBySymbol(symbol)
