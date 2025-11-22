from datetime import datetime
from dataclasses import dataclass


@dataclass
class Candle:
    symbol: str
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
