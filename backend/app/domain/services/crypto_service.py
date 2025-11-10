# app/domain/services/crypto_service.py
class CryptoService:
    def __init__(self, repository):
        self.repository = repository

    async def get_crypto_price(self, symbol: str) -> float:
        return await self.repository.get_price(symbol)
