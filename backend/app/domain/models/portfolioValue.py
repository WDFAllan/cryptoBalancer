from dataclasses import dataclass
from datetime import datetime


@dataclass
class PortfolioValue:
    id: int | None
    userId: int
    date: datetime
    totalValue: float

