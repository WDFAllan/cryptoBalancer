import httpx

class CryptoRepository:
    BASE_URL = "https://api.binance.com/api/v3/ticker/price"

    async def get_price(self, symbol: str) -> float:
        """
        Récupère le prix actuel d'une crypto depuis Binance.
        Binance utilise le format SYMBOLUSDT, par exemple BTCUSDT.
        """
        symbol = symbol.upper() + "USDT"  # ex: BTC -> BTCUSDT
        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()
            return float(data["price"])