from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem


client = TestClient(app)


def test_create_wallet_success():
    mock_wallet = Wallet(id=1, userId=1, items=[])

    with patch("app.api.v1.controllers.walletController.WalletService") as MockService:
        mock_service = MagicMock()
        mock_service.createWalletForUser.return_value = mock_wallet
        MockService.return_value = mock_service

        response = client.post("/api/v1/wallet/1/create")

        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == 1
        assert data["items"] == []


def test_create_wallet_error():
    with patch("app.api.v1.controllers.walletController.WalletService") as MockService:
        mock_service = MagicMock()
        mock_service.createWalletForUser.side_effect = Exception("Wallet creation failed")
        MockService.return_value = mock_service

        response = client.post("/api/v1/wallet/1/create")

        assert response.status_code == 400
        assert "Wallet creation failed" in response.json()["detail"]


def test_get_wallet_by_user_id_success():
    mock_wallet = Wallet(
        id=1,
        userId=2,
        items=[WalletItem(id=1, symbol="BTC", amount=1.5)]
    )

    with patch("app.api.v1.controllers.walletController.WalletService") as MockService:
        mock_service = MagicMock()
        mock_service.getWalletByUserId.return_value = mock_wallet
        MockService.return_value = mock_service

        response = client.get("/api/v1/wallet/getWalletByUserId/2")

        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == 2
        assert len(data["items"]) == 1
        assert data["items"][0]["symbol"] == "BTC"


def test_add_item_to_wallet_success():
    mock_wallet = Wallet(
        id=1,
        userId=3,
        items=[WalletItem(id=1, symbol="ETH", amount=2.0)]
    )

    with patch("app.api.v1.controllers.walletController.WalletService") as MockService:
        mock_service = MagicMock()
        mock_service.addItemToWallet.return_value = mock_wallet
        MockService.return_value = mock_service

        response = client.post("/api/v1/wallet/3/addItemToWalletByUserID?symbol=ETH&amount=2.0")

        assert response.status_code == 200
        data = response.json()
        assert data["userId"] == 3
        assert len(data["items"]) == 1
        assert data["items"][0]["symbol"] == "ETH"
        assert data["items"][0]["amount"] == 2.0
