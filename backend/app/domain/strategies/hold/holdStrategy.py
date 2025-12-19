import pandas as pd

from app.domain.strategies.baseStrategy import BaseStrategy
from app.domain.strategies.tradingUtils.Utils import wallet_items_to_holdings


class holdStrategy(BaseStrategy):

    def run(self, prices:pd.DataFrame,wallet:dict) -> pd.DataFrame:
        wallet_holdings = wallet_items_to_holdings(wallet, quote="EUR")

        # Quantité de chaque actif acheté au départ
        quantities = wallet_holdings

        # Valeur du portefeuille au fil du temps
        values = (prices[list(quantities.keys())] * pd.Series(quantities)).sum(axis=1)
        df = pd.DataFrame({"value": values})
        df.index.name = "date"
        return df