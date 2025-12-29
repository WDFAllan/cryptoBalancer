from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_price_returns_value():
    with patch("app.api.v1.controllers.cryptoController.service") as mock_service:
        mock_service.get_crypto_price = AsyncMock(return_value=42000.0)

        resp = client.get("/api/v1/crypto/price/BTC")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "BTC"
        assert data["price"] == 42000.0


def test_get_all_symbols_returns_list():
    with patch("app.api.v1.controllers.cryptoController.service") as mock_service:
        mock_service.get_all_symbols = AsyncMock(return_value=["BTCEUR", "ETHEUR"])

        resp = client.get("/api/v1/crypto/getAllSymbols")
        assert resp.status_code == 200
        assert resp.json()["symbols"] == ["BTCEUR", "ETHEUR"]
