from dataclasses import dataclass
from typing import Optional


@dataclass
class WalletItem:
    id: int | None
    symbol: str
    amount: float
