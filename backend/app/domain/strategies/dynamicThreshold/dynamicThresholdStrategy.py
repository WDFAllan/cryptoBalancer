from typing import Dict

from app.domain.strategies.baseStrategy import BaseStrategy
import pandas as pd
import numpy as np
from app.domain.strategies.tradingUtils.Broker import Broker, TradeCost
from app.domain.strategies.tradingUtils.Utils import (
    normalize_weights, 
    wallet_items_to_holdings,
    compute_portfolio_value,
    moving_volatility
)
from app.domain.strategies.dynamicThreshold.dynamicThresholdParams import DynamicThresholdParams


class DynamicThresholdStrategy(BaseStrategy):

    def __init__(self, params: DynamicThresholdParams):
        self.params = params
        self.params.target_weights = {
            k: v for k, v in self.params.target_weights.items() if v > 0
        }
        self.params.target_weights = normalize_weights(self.params.target_weights)
        self.last_rebalance_day = 0  # Jour du dernier rééquilibrage

    def run(self, prices: pd.DataFrame, wallet: dict) -> pd.DataFrame:
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

        # Rééquilibrage initial
        tw0 = self.target_weights(t0, prices)
        c0 = broker.rebalance(t0, tw0)
        broker.mark_to_market(t0, extra_cost=c0, target_weights=tw0)
        self.last_rebalance_day = t0

        # Initialisation de la volatilité
        portfolio_values = self._compute_portfolio_value_history(broker, prices)
        portfolio_volatility = self._compute_portfolio_volatility(portfolio_values, p.vol_window)

        # Boucle temporelle
        for t in range(1, len(prices)):
            tw = self.target_weights(t, prices)
            cw = broker._current_weights(t)
            
            # Calcul du drift par actif (avec seuils différents pour actifs stables)
            drifts = {}
            for asset in prices.columns:
                if asset in cw or asset in tw:
                    drift = abs(cw.get(asset, 0.0) - tw.get(asset, 0.0))
                    drifts[asset] = drift

            # Calcul de la volatilité du portefeuille (mise à jour périodiquement)
            if t == 1 or (t - self.last_rebalance_day) % max(1, p.vol_window // 5) == 0:
                portfolio_values = self._compute_portfolio_value_history(broker, prices)
                portfolio_volatility = self._compute_portfolio_volatility(portfolio_values, p.vol_window)

            # Récupération de la volatilité actuelle
            current_vol = 0.0
            if len(portfolio_volatility) > 0:
                if t < len(portfolio_volatility):
                    current_vol = portfolio_volatility.iloc[t]
                else:
                    current_vol = portfolio_volatility.iloc[-1]

            # Calcul du seuil dynamique pour actifs non-stables
            dynamic_threshold = self._compute_dynamic_threshold(current_vol)

            # Vérification des conditions de rééquilibrage
            # On vérifie si au moins un actif dépasse son seuil (stable ou dynamique)
            should_rebalance = False
            max_drift = 0.0
            for asset, drift in drifts.items():
                max_drift = max(max_drift, drift)
                if asset in p.stable_assets:
                    if drift >= p.stable_threshold:
                        should_rebalance = True
                else:
                    if drift >= dynamic_threshold:
                        should_rebalance = True

            days_since_rebalance = t - self.last_rebalance_day
            cooldown_met = days_since_rebalance >= p.cooldown_days

            if p.verbose and t % 10 == 0:
                print(f"\n[{prices.index[t].date()}] Drift max: {max_drift:.4f}, "
                      f"Seuil dynamique: {dynamic_threshold:.4f}, "
                      f"Seuil stable: {p.stable_threshold:.4f}, "
                      f"Volatilité: {current_vol:.4f}, "
                      f"Cooldown: {days_since_rebalance}/{p.cooldown_days}")

            if cooldown_met and should_rebalance:
                # Rééquilibrage partiel ou complet selon rebal_frac
                if p.rebal_frac < 1.0:
                    # Rééquilibrage partiel : on ajuste les poids cibles
                    tw_partial = self._compute_partial_rebalance_weights(cw, tw, p.rebal_frac)
                    c = broker.rebalance(t, tw_partial)
                    broker.mark_to_market(t, extra_cost=c, target_weights=tw)
                else:
                    # Rééquilibrage complet
                    c = broker.rebalance(t, tw)
                    broker.mark_to_market(t, extra_cost=c, target_weights=tw)
                self.last_rebalance_day = t
            else:
                broker.mark_to_market(t, extra_cost=0.0, target_weights=tw)

        return broker.get_history()

    def target_weights(self, t: int, prices: pd.DataFrame) -> Dict[str, float]:
        """Renvoie les poids cibles à la date t (identiques chaque jour, filtrés aux colonnes disponibles)."""
        cols = set(prices.columns)
        tw = {a: w for a, w in self.params.target_weights.items() if a in cols}
        return normalize_weights(tw)

    def _compute_dynamic_threshold(self, current_volatility: float) -> float:
        """
        Calcule le seuil dynamique basé sur la volatilité actuelle du portefeuille.
        Formule: threshold = min_th + k * volatility
        """
        p = self.params
        
        # Calcul du seuil : min_th + k * volatilité
        # Plus la volatilité est élevée, plus le seuil augmente
        threshold = p.min_th + p.k * current_volatility
        
        # Application des limites min/max
        threshold = max(p.min_th, min(p.max_th, threshold))
        
        return threshold

    def _compute_partial_rebalance_weights(
        self, 
        current_weights: Dict[str, float], 
        target_weights: Dict[str, float],
        rebal_frac: float
    ) -> Dict[str, float]:
        """
        Calcule les poids pour un rééquilibrage partiel.
        Nouveau poids = poids_actuel + frac * (poids_cible - poids_actuel)
        """
        partial_weights = {}
        for asset in set(current_weights.keys()) | set(target_weights.keys()):
            current = current_weights.get(asset, 0.0)
            target = target_weights.get(asset, 0.0)
            partial = current + rebal_frac * (target - current)
            partial_weights[asset] = partial
        
        # Normalisation pour s'assurer que la somme vaut 1
        return normalize_weights(partial_weights)

    def _compute_portfolio_value_history(self, broker: Broker, prices: pd.DataFrame) -> pd.Series:
        """Calcule l'historique des valeurs du portefeuille."""
        values = []
        for t in range(len(prices)):
            val = broker._portfolio_value(t)
            values.append(val)
        return pd.Series(values, index=prices.index)

    def _compute_portfolio_volatility(self, portfolio_values: pd.Series, window: int) -> pd.Series:
        """Calcule la volatilité du portefeuille sur une fenêtre glissante."""
        if len(portfolio_values) < 2:
            return pd.Series([0.0] * len(portfolio_values), index=portfolio_values.index)
        
        # Calcul des rendements logarithmiques
        log_returns = np.log(portfolio_values).diff()
        
        # Volatilité annualisée (en supposant des données quotidiennes)
        volatility = log_returns.rolling(window=window, min_periods=min(5, window)).std() * np.sqrt(365)
        
        # Remplir les NaN avec 0 ou la première valeur valide
        volatility = volatility.bfill().fillna(0.0)
        
        return volatility

