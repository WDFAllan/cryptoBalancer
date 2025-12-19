import pandas as pd

from app.domain.strategies.hold.holdParams import HoldParams
from app.domain.strategies.hold.holdStrategy import holdStrategy


class HoldRunner:

    def run(self,prices:pd.DataFrame,wallet:dict):
        strategy = holdStrategy()
        return strategy.run(prices, wallet)