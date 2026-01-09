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

        # Pré-calcul de la volatilité annualisée pour tous les actifs (optimisation)
        # DataFrame avec colonnes = actifs, index = dates
        vol_ann = self._precompute_asset_volatilities(prices, p.vol_window)

        # Boucle temporelle
        for t in range(1, len(prices)):
            tw = self.target_weights(t, prices)
            cw = broker._current_weights(t)
            
            # Calcul du drift par actif
            drifts = {}
            for asset in prices.columns:
                if asset in cw or asset in tw:
                    drift = abs(cw.get(asset, 0.0) - tw.get(asset, 0.0))
                    drifts[asset] = drift

            # Calcul des seuils par actif (thr[a])
            thresholds = {}
            current_date = prices.index[t]
            
            for asset in prices.columns:
                if asset in p.stable_assets:
                    # Seuil fixe pour les actifs stables
                    thresholds[asset] = p.stable_threshold
                else:
                    # Seuil dynamique basé sur la volatilité de l'actif
                    # Utiliser l'index pour récupérer la volatilité à la date t
                    if current_date in vol_ann.index and asset in vol_ann.columns:
                        vol_a = vol_ann.loc[current_date, asset]
                    else:
                        vol_a = 0.0
                    
                    # Formule: thr[a] = clamp(min_th + k * vol[a], min_th, max_th)
                    thr_a = p.min_th + p.k * vol_a
                    # Clamp entre min_th et max_th
                    thresholds[asset] = max(p.min_th, min(p.max_th, thr_a))

            # Vérification des conditions de rééquilibrage
            # Déclenchement si au moins un actif dépasse son seuil
            should_rebalance = False
            max_drift = 0.0
            for asset, drift in drifts.items():
                max_drift = max(max_drift, drift)
                if asset in thresholds and drift >= thresholds[asset]:
                    should_rebalance = True

            days_since_rebalance = t - self.last_rebalance_day
            cooldown_met = days_since_rebalance >= p.cooldown_days

            if p.verbose and t % 10 == 0:
                # Afficher quelques seuils pour debug
                sample_thresholds = {a: thresholds.get(a, 0.0) for a in list(thresholds.keys())[:3]}
                print(f"\n[{prices.index[t].date()}] Drift max: {max_drift:.4f}, "
                      f"Seuils (échantillon): {sample_thresholds}, "
                      f"Cooldown: {days_since_rebalance}/{p.cooldown_days}")

            if cooldown_met and should_rebalance:
                # Rééquilibrage partiel ou complet selon rebal_frac
                if p.rebal_frac < 1.0:
                    # Rééquilibrage partiel : on ajuste les poids cibles
                    tw_partial = self._compute_partial_rebalance_weights(cw, tw, p.rebal_frac)
                    # Vérification que tw_partial est bien normalisé (déjà fait dans la fonction)
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

    def _precompute_asset_volatilities(
        self, 
        prices: pd.DataFrame, 
        window: int
    ) -> pd.DataFrame:
        """
        Pré-calcule la volatilité annualisée pour chaque actif sur une fenêtre glissante.
        
        Retourne un DataFrame avec:
        - Colonnes = actifs (même que prices.columns)
        - Index = dates (même que prices.index)
        - Valeurs = volatilité annualisée à chaque date
        
        Formule pour chaque actif a:
        - log_returns[a] = log(prices[a]).diff()
        - vol[a] = std(log_returns[a] over window) * sqrt(365)
        
        Performance: Calcul une seule fois au début, puis lecture O(1) dans la boucle.
        """
        vol_df = pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)
        
        for asset in prices.columns:
            # Calcul des rendements logarithmiques
            log_returns = np.log(prices[asset]).diff()
            
            # Volatilité annualisée sur fenêtre glissante
            # rolling(window).std() calcule l'écart-type sur la fenêtre
            vol_series = log_returns.rolling(window=window, min_periods=min(5, window)).std() * np.sqrt(365)
            
            # Remplir les NaN avec 0 ou la première valeur valide
            vol_series = vol_series.bfill().fillna(0.0)
            
            vol_df[asset] = vol_series
        
        return vol_df

