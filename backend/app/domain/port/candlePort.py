from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List


class ICandlePort(ABC):

    @abstractmethod
    async def saveCandles(self, symbol: str, candles: List[Dict]):
        pass

    @abstractmethod
    async def deleteOlderThan(self, symbol: str, date: datetime):
        pass

    @abstractmethod
    async def getCandlesBySymbol(self, symbol: str):
        pass