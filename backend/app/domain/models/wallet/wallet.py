from dataclasses import dataclass, field
from typing import List, Optional

from app.domain.models.wallet.walletItem import WalletItem


@dataclass
class Wallet:
    id: Optional[int]
    userId: int
    strategy: Optional[str] = None
    items: List[WalletItem] = field(default_factory=list)