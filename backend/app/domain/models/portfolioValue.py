from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PortfolioValue:
    id: Optional[int]
    userId: int
    date: datetime
    totalValue: float
    createdAt: Optional[datetime] = None
