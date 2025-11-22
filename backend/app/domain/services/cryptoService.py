# app/domain/services/cryptoService.py
from typing import List

from app.domain.port.cryptoPort import ICryptoPort


class CryptoService:
    def __init__(self, repository:ICryptoPort):
        self.repository = repository

    async def get_crypto_price(self, symbol: str) -> float:
        return await self.repository.get_price(symbol)

    async def get_all_symbols(self) -> List[str]:
        return await self.repository.get_all_symbols()