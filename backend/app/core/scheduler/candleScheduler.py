from fastapi_utils.tasks import repeat_every
from sqlalchemy import True_

from app.core.database.database import SessionLocal
from app.domain.services.candleService import CandleService
from app.infrastructure.adapters.binanceCandleAdapter import binanceCandleAdapter
from app.infrastructure.repository.candleRepository import CandleRepository
from app.infrastructure.repository.cryptoRepository import CryptoRepository


def registerCandleScheduler(app):

    db = SessionLocal()

    candle_repo = CandleRepository(db)
    crypto_repo = CryptoRepository()
    candle_provider = binanceCandleAdapter()

    candle_service = CandleService(
        candleRepo=candle_repo,
        cryptoRepo=crypto_repo,
        binanceCandleAdapter=candle_provider
    )

    @app.on_event("startup")
    @repeat_every(seconds=60 * 60 * 24, wait_first=True)
    async def sync_candles():
        print("Synchronisation automatique des bougies…")
        await candle_service.syncLastTwoYears()
        print("✅Synchronisation terminée.")