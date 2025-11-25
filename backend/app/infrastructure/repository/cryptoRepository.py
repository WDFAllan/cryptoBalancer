from typing import List

import httpx

from app.domain.port.cryptoPort import ICryptoPort


class CryptoRepository(ICryptoPort):
    BASE_URL = "https://api.binance.com/api/v3"

    async def get_price(self, symbol: str) -> float:

        endpoint = self.BASE_URL + "/ticker/price"
        symbol = symbol.upper() + "USDT"  # ex: BTC -> BTCUSDT

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()

            return float(data["price"])

    async def get_all_symbols(self) -> List[str]:

        # endpoint = self.BASE_URL + "/exchangeInfo"
        #
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(endpoint)
        #     response.raise_for_status()
        #     data = response.json()
        #
        #     symbols = sorted([s["symbol"] for s in data["symbols"] if s["symbol"].endswith("EUR")])

        symbols = ["BTCEUR", "ETHEUR", "BNBEUR", "XRPEUR", "SOLEUR"]
        return symbols
