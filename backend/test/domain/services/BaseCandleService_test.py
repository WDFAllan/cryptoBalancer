from datetime import timedelta
from unittest.mock import Mock, AsyncMock

import pytest

from app.domain.services.candle.baseCandleService import baseCandleService


@pytest.mark.asyncio
async def test_sync_period_saves_candles_for_each_symbol():
    candleRepo = AsyncMock()
    cryptoRepo = AsyncMock()
    binanceAdapter = Mock()

    cryptoRepo.get_all_symbols.return_value = ["BTCEUR", "ETHEUR", "BNBEUR", "XRPEUR", "SOLEUR"]
    binanceAdapter.fetchCandles.return_value = ["candle"]

    service = baseCandleService(
        candleRepo=candleRepo,
        cryptoRepo=cryptoRepo,
        binanceAdapter=binanceAdapter,
        timeframe="1d",
        retention_days=30
    )

    await service.syncPeriod(7)

    assert binanceAdapter.fetchCandles.call_count == 5
    assert candleRepo.saveCandles.call_count == 5

@pytest.mark.asyncio
async def test_update_candles_saves_and_cleans():
    crypto_repo = AsyncMock()
    candle_repo = AsyncMock()
    binance_adapter = Mock()

    crypto_repo.get_all_symbols.return_value = ["BTC"]
    binance_adapter.fetchCandles.return_value = ["candle"]

    service = baseCandleService(
        candleRepo=candle_repo,
        cryptoRepo=crypto_repo,
        binanceAdapter=binance_adapter,
        timeframe="1d",
        retention_days=30
    )

    await service.updateCandles()

    candle_repo.saveCandles.assert_called_once()
    candle_repo.deleteOlderThan.assert_called_once()

@pytest.mark.asyncio
async def test_update_candles_skips_when_no_data():
    crypto_repo = AsyncMock()
    candle_repo = AsyncMock()
    binance_adapter = Mock()

    crypto_repo.get_all_symbols.return_value = ["BTC"]
    binance_adapter.fetchCandles.return_value = []

    service = baseCandleService(
        candleRepo=candle_repo,
        cryptoRepo=crypto_repo,
        binanceAdapter=binance_adapter,
        timeframe="1d",
        retention_days=30
    )

    await service.updateCandles()

    candle_repo.saveCandles.assert_not_called()
    candle_repo.deleteOlderThan.assert_not_called()

@pytest.mark.asyncio
async def test_update_candles_ignores_exceptions():
    crypto_repo = AsyncMock()
    candle_repo = AsyncMock()
    binance_adapter = Mock()

    crypto_repo.get_all_symbols.return_value = ["BTC", "ETH"]
    binance_adapter.fetchCandles.side_effect = Exception("Binance down")

    service = baseCandleService(
        candleRepo=candle_repo,
        cryptoRepo=crypto_repo,
        binanceAdapter=binance_adapter,
        timeframe="1d",
        retention_days=30
    )

    await service.updateCandles()

    candle_repo.saveCandles.assert_not_called()


def test_timeframe_to_delta_days():
    service = baseCandleService(None, None, None, "1d", 30)
    assert service._timeframe_to_delta() == timedelta(days=1)


def test_timeframe_to_delta_minutes():
    service = baseCandleService(None, None, None, "3m", 30)
    assert service._timeframe_to_delta() == timedelta(minutes=3)


def test_timeframe_to_delta_invalid():
    service = baseCandleService(None, None, None, "1h", 30)

    with pytest.raises(ValueError):
        service._timeframe_to_delta()
