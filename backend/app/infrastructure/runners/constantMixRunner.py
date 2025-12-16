import pandas as pd
from typing import Dict

from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy

class ConstantMixRunner:

    def run(self, prices: pd.DataFrame):
        params = ConstantMixParams(
            target_weights={"BTCEUR": 0.8, "ETHEUR": 0.2,"SOLEUR":0,"XRPEUR":0,"BNBEUR":0},
            initial_capital=10000,
            fee_rate=0.001,
            fixed_fee=1,
            slippage=0.0002,
            rebalance="M",
            verbose=False,
            drift_threshold=0
        )
        strategy = ConstantMixStrategy(params)
        return strategy.run(prices)