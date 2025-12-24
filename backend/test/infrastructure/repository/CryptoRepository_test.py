import pytest
import respx

from app.infrastructure.repository.cryptoRepository import CryptoRepository


@pytest.mark.asyncio
async def test_get_all_symbols_repository():
    repo = CryptoRepository()

    symbols = await repo.get_all_symbols()

    assert isinstance(symbols, list)
    assert len(symbols) == 5
    assert "BTCEUR" in symbols

@pytest.mark.asyncio
@respx.mock
async def test_get_prices_repository():
    repo = CryptoRepository()

    respx.get("https://api.binance.com/api/v3/ticker/price",
              params={"symbol":"BTCEUR"}
    ).respond(
        json={"symbol":"BTCEUR","price":42000.0}
    )

    price = await repo.get_price("BTCEUR")
    assert price == 42000.0