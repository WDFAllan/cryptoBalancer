from abc import ABC, abstractmethod
from typing import List

class ICryptoPort(ABC):

    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        pass

    @abstractmethod
    async def get_all_symbols(self) -> List[str]:
        pass