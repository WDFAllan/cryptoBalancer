from dataclasses import dataclass
from typing import Dict

@dataclass
class HoldParams:
    verbose: bool = False
    fee_rate: float = 0.0
    slippage: float = 0.0
    favorite_platform: str = "Binance"  # Pour cohérence avec autres stratégies
