from unittest.mock import Mock

import pytest

from app.domain.models.wallet.wallet import Wallet
from app.domain.services.walletService import WalletService


def test_create_wallet_when_user_has_no_wallet():

    walletRepo = Mock()
    walletRepo.getWalletByUserId.return_value = None

    expected_wallet = Wallet(id=1,userId=42)
    walletRepo.createWallet.return_value = expected_wallet

    service = WalletService(walletRepo)

    wallet = service.createWalletForUser(user_id=42)

    walletRepo.getWalletByUserId.assert_called_once_with(42)
    walletRepo.createWallet.assert_called_once_with(42)
    assert wallet == expected_wallet

def test_create_wallet_when_user_has_wallet():
    walletRepo = Mock()
    walletRepo.getWalletByUserId.return_value = Wallet(id=1,userId=42)

    service = WalletService(walletRepo)

    with pytest.raises(Exception) as exc:
        service.createWalletForUser(user_id=42)

    assert "already has a wallet" in str(exc.value)
    walletRepo.createWallet.assert_not_called()

def test_create_wallet_raises_if_user_id_invalid():
    walletRepo = Mock()
    service = WalletService(walletRepo)

    with pytest.raises(Exception) as exc:
        service.createWalletForUser(user_id=0)

    walletRepo.getWalletByUserId.assert_not_called()
    walletRepo.createWallet.assert_not_called()

def test_add_to_wallet():
    walletRepo = Mock()
    expectedWallet = Wallet(id=1,userId=42,items=[])

    walletRepo.addToWallet.return_value = expectedWallet

    service = WalletService(walletRepo)

    result = service.addItemToWallet(
        user_id=42,
        symbol="BTCEUR",
        amount=1
    )

    assert result == expectedWallet

    walletRepo.addToWallet.assert_called_once()

    called_user_id, called_item = walletRepo.addToWallet.call_args[0]

    assert called_user_id == 42
    assert called_item.symbol == "BTCEUR"
    assert called_item.amount == 1
    assert called_item.id is None

def test_add_to_wallet_wrong_user_id():
    walletRepo = Mock()
    service = WalletService(walletRepo)

    walletRepo.addToWallet.side_effect = ValueError("User not found")

    with pytest.raises(ValueError) as exc:
        service.addItemToWallet(
            user_id=42,
            symbol="BTCEUR",
            amount=1
        )

    walletRepo.addToWallet.assert_called_once()

def test_add_to_wallet_negative_amount():
    walletRepo = Mock()
    service = WalletService(walletRepo)

    with pytest.raises(ValueError) as exc:
        service.addItemToWallet(
            user_id=42,
            symbol="BTCEUR",
            amount=-1
        )

    walletRepo.addToWallet.assert_not_called()

