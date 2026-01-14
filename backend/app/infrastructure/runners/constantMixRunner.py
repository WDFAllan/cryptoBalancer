import pandas as pd
from typing import Dict

from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy

class ConstantMixRunner:
    def run(self, prices: pd.DataFrame, wallet: dict, fee_rate: float = 0.001, slippage: float = 0.0002, favorite_platform: str = "Binance"):
        params = ConstantMixParams(
            target_weights={"BTCEUR": 0.8, "ETHEUR": 0.2, "SOLEUR": 0, "XRPEUR": 0, "BNBEUR": 0},
            fee_rate=fee_rate,
            fixed_fee=1,
            slippage=slippage,
            rebalance="M",
            verbose=False,
            drift_threshold=0,
            favorite_platform=favorite_platform
        )
        strategy = ConstantMixStrategy(params)
        return strategy.run(prices, wallet)
