

@dataclass
class WalletTransaction:
    id: int | None
    walletId: int
    transactionType: TransactionType
    symbol: str
    amount: float
    previousAmount: float | None
    reason: str | None
    timestamp: datetime