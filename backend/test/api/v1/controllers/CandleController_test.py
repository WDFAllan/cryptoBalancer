from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.controllers import candleController

client = TestClient(app)


def test_get_two_years_candles_calls_service():
    mock_service = MagicMock()
    mock_service.syncPeriod = AsyncMock(return_value={"synced": True})

    app.dependency_overrides[candleController.candle1d_service] = lambda db=None: mock_service
    try:
        resp = client.get("/api/v1/candle/getTwoYearsCandles")
        assert resp.status_code == 200
        assert resp.json() == {"synced": True}
    finally:
        app.dependency_overrides.pop(candleController.candle1d_service, None)


def test_get_candles_by_symbol_calls_service():
    mock_service = MagicMock()
    mock_service.getCandlesBySymbol.return_value = [{"ts": 1}]

    app.dependency_overrides[candleController.candle1d_service] = lambda db=None: mock_service
    try:
        resp = client.get("/api/v1/candle/getCandlesBySymbol/BTCEUR")
        assert resp.status_code == 200
        assert resp.json() == [{"ts": 1}]
    finally:
        app.dependency_overrides.pop(candleController.candle1d_service, None)


def test_three_minute_candles_calls_service():
    mock_service = MagicMock()
    mock_service.syncPeriod = AsyncMock(return_value={"synced": True})

    app.dependency_overrides[candleController.candle3m_service] = lambda db=None: mock_service
    try:
        resp = client.get("/api/v1/candle/getThreeMinutesCandles")
        assert resp.status_code == 200
        assert resp.json() == {"synced": True}
    finally:
        app.dependency_overrides.pop(candleController.candle3m_service, None)

def test_get_three_minute_candles_by_symbol_calls_service():
    mock_service = MagicMock()
    mock_service.getCandlesBySymbol.return_value = [{"ts": 3}]

    app.dependency_overrides[candleController.candle3m_service] = lambda db=None: mock_service
    try:
        resp = client.get("/api/v1/candle/getCandles3MBySymbol/ETHEUR")
        assert resp.status_code == 200
        assert resp.json() == [{"ts": 3}]
    finally:
        app.dependency_overrides.pop(candleController.candle3m_service, None)