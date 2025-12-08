from fastapi_utils.tasks import repeat_every

from app.core.database.database import SessionLocal
from app.domain.services.candle.baseCandleService import baseCandleService
from app.infrastructure.adapters.binanceCandleAdapter import binanceCandleAdapter
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.repository.candle.threeMinCandleRepository import threeMinCandleRepository
from app.infrastructure.repository.cryptoRepository import CryptoRepository


def registerCandleScheduler(app):

    db = SessionLocal()

    # candle_repo = threeMinCandleRepository(db)
    candle_repo = dailyCandleRepository(db)
    crypto_repo = CryptoRepository()
    candle_provider = binanceCandleAdapter()

    candle_service = baseCandleService(
        candleRepo=candle_repo,
        cryptoRepo=crypto_repo,
        binanceAdapter=candle_provider,
        timeframe="1d",
        retention_days=730
    )

    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24, wait_first=True)
    async def sync_candles():
        print("Synchronisation journalière automatique des bougies…")
        await candle_service.syncPeriod(730)
        print("✅Synchronisation terminée.")

    # @app.on_event("startup")
    # @repeat_every(seconds=60 * 3, wait_first=True)
    # async def sync_3min_candles():
    #     print("Synchronisation 3min automatique des bougies…")
    #     await candle_service.updateCandles()
    #     print("✅Synchronisation terminée.")