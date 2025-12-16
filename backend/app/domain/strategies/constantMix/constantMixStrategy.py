from typing import Dict

from app.domain.strategies.baseStrategy import BaseStrategy
import pandas as pd
from app.domain.strategies.tradingUtils.Broker import Broker, TradeCost
from app.domain.strategies.tradingUtils.Utils import normalize_weights, wallet_items_to_holdings, \
    compute_portfolio_value
from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams



class ConstantMixStrategy(BaseStrategy):

    def __init__(self,params: ConstantMixParams):
        self.params = params
        self.params.target_weights = {
            k: v for k, v in self.params.target_weights.items() if v > 0
        }
        self.params.target_weights = normalize_weights(self.params.target_weights)

    def run(self, prices:pd.DataFrame,wallet:dict) -> pd.DataFrame:
        p = self.params
        cost = TradeCost(fee_rate=p.fee_rate, fixed_fee=p.fixed_fee, slippage=p.slippage)
        broker = Broker(prices=prices, trade_cost=cost, verbose=p.verbose)

        # Déploiement initial (t0)
        t0 = 0
        p0 = prices.iloc[t0]

        wallet_holdings = wallet_items_to_holdings(wallet, quote="EUR")

        for asset, qty in wallet_holdings.items():
            if asset in broker.holdings:
                broker.holdings[asset] = qty

        initial_capital = compute_portfolio_value(broker.holdings, p0)

        if initial_capital <= 0:
            raise ValueError("Wallet utilisateur vide ou prix manquants")

        if p.verbose:
            print(f"\n[{prices.index[t0].date()}] Wallet initial chargé")
            print(f"  Capital réel : {initial_capital:.2f} €")
            print("  Holdings    : " + ", ".join(
                f"{a}={q:.6f}" for a, q in broker.holdings.items() if q > 0
            ))

            # =========================
            # 3️⃣ RÉÉQUILIBRAGE INITIAL
            # =========================
        tw0 = self.target_weights(t0, prices)

        c0 = broker.rebalance(t0, tw0)
        broker.mark_to_market(t0, extra_cost=c0, target_weights=tw0)

        # =========================
        # 4️⃣ BOUCLE TEMPORELLE
        # =========================
        for t in range(1, len(prices)):
            tw = self.target_weights(t, prices)

            cw = broker._current_weights(t)
            max_drift = max(
                abs(cw.get(a, 0.0) - tw.get(a, 0.0))
                for a in prices.columns
                if a in cw or a in tw
            )

            scheduled = self._is_rebalance_day(prices.index, t, p.rebalance)
            drift_hit = (
                    p.drift_threshold is not None
                    and max_drift >= p.drift_threshold
            )

            if scheduled or drift_hit:
                c = broker.rebalance(t, tw)
                broker.mark_to_market(t, extra_cost=c, target_weights=tw)
            else:
                broker.mark_to_market(t, extra_cost=0.0, target_weights=tw)

        return broker.get_history()

    def target_weights(self, t: int, prices: pd.DataFrame) -> Dict[str, float]:
        """Renvoie les poids cibles à la date t (identiques chaque jour, filtrés aux colonnes disponibles)."""
        cols = set(prices.columns)
        tw = {a: w for a, w in self.params.target_weights.items() if a in cols}
        # s'il manque un actif dans les données, on renormalise
        return normalize_weights(tw)

    @staticmethod
    def _is_rebalance_day(idx: pd.DatetimeIndex, t: int, mode: str) -> bool:
        """Décide si on rééquilibre à la date t selon la fréquence choisie."""
        if t == 0:
            return False  # déploiement initial géré à part

        mode = mode.upper()
        if mode == "D":
            return True
        if mode == "W":
            # nouveau numéro de semaine
            return idx[t].isocalendar().week != idx[t - 1].isocalendar().week
        if mode == "M":
            # changement de mois
            return (idx[t].month != idx[t - 1].month) or (idx[t].year != idx[t - 1].year)
        if mode == "Q" or mode == "3M":
            # changement de trimestre
            return idx[t].to_period("Q") != idx[t - 1].to_period("Q")
        # format "7D", "10D", ...
        if mode.endswith("D") and mode[:-1].isdigit():
            k = int(mode[:-1])
            return (t % k) == 0
        # par défaut: quotidien
        return True