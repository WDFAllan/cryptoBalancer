from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from app.domain.models.portfolioValue import PortfolioValue


class IPortfolioValuePort(ABC):

    @abstractmethod
    def create(self, userId: int, date: datetime, totalValue: float) -> PortfolioValue:
        pass

    @abstractmethod
    def getByUserId(self, userId: int) -> List[PortfolioValue]:
        pass

    @abstractmethod
    def getByUserIdAndDateRange(self, userId: int, startDate: datetime, endDate: datetime) -> List[PortfolioValue]:
        pass

    @abstractmethod
    def getLatestByUserId(self, userId: int) -> PortfolioValue | None:
        pass

