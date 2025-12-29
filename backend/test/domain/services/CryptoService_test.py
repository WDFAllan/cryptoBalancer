from unittest.mock import AsyncMock

import pytest

from app.domain.services.cryptoService import CryptoService


@pytest.mark.asyncio
async def test_get_crypto_price_calls_service():
    repo = AsyncMock()
    repo.get_price.return_value = 42000.0

    service = CryptoService(repository=repo)

    price = await service.get_crypto_price("BTC")

    repo.get_price.assert_awaited_once_with("BTC")
    assert price == 42000.0

@pytest.mark.asyncio
async def test_get_all_symbols_service():
    repo = AsyncMock()
    repo.get_all_symbols.return_value = ["BTCEUR", "ETHEUR", "BNBEUR", "XRPEUR", "SOLEUR"]

    service = CryptoService(repository=repo)

    symbols = await service.get_all_symbols()

    repo.get_all_symbols.assert_awaited_once()
    assert symbols == ["BTCEUR", "ETHEUR", "BNBEUR", "XRPEUR", "SOLEUR"]