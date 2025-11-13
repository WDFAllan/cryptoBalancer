from dataclasses import dataclass,field
from typing import List

from app.domain.models.wallet.walletItem import WalletItem


@dataclass
class Wallet:
    id:int | None
    userId: int
    items: List[WalletItem] = field(default_factory=list)