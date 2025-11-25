from datetime import datetime, timedelta, timezone

from app.domain.port.candlePort import ICandlePort
from app.domain.port.cryptoPort import ICryptoPort
from app.domain.services.candle.baseCandleService import baseCandleService


class dailyCandleService(baseCandleService):
    def __init__(self, candleRepo, cryptoRepo, binanceAdapter):
        super().__init__(
            candleRepo,
            cryptoRepo,
            binanceAdapter,
            timeframe="1d",
            retention_days=730
        )


    def getCandlesBySymbol(self, symbol: str):
        return self.candleRepo.getCandlesBySymbol(symbol)