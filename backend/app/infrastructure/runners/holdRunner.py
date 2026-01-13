import pandas as pd
from app.domain.strategies.hold.holdParams import HoldParams
from app.domain.strategies.hold.holdStrategy import holdStrategy

class HoldRunner:
    def run(self, prices: pd.DataFrame, wallet: dict, fee_rate: float = 0.0, slippage: float = 0.0):
        params = HoldParams(fee_rate=fee_rate, slippage=slippage)
        strategy = holdStrategy(params)
        return strategy.run(prices, wallet)
