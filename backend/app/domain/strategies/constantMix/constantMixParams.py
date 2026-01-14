from dataclasses import dataclass
from typing import Dict


@dataclass
class ConstantMixParams:
    target_weights: Dict[str, float] = None
    initial_capital: float = 10000.0
    fee_rate: float = 0.001
    fixed_fee: float = 1.0
    slippage: float = 0.0002
    rebalance: str = "M"
    verbose: bool = False
    drift_threshold: float = 0
    favorite_platform: str = "Binance"  # Plateforme pour calculer slippage par asset