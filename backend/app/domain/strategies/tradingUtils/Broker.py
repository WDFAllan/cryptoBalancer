# core/broker.py
import pandas as pd
import numpy as np

class TradeCost:
    def __init__(self, fee_rate: float = 0.001, fixed_fee: float = 1.0, slippage: float = 0.0002):
        self.fee_rate = fee_rate
        self.fixed_fee = fixed_fee
        self.slippage = slippage

    def compute(self, trade_values: dict[str, float]) -> float:
        variable_cost = sum(abs(v) * self.fee_rate for v in trade_values.values())
        fixed_cost = self.fixed_fee * len([v for v in trade_values.values() if abs(v) > 1e-10])
        return variable_cost + fixed_cost


# --- additions / modifications dans core/broker.py ---

class Broker:
    def __init__(self, prices: pd.DataFrame, trade_cost: TradeCost, verbose: bool = False):
        self.prices = prices
        self.assets = prices.columns.tolist()
        self.trade_cost = trade_cost
        self.verbose = verbose

        self.holdings = {a: 0.0 for a in self.assets}
        self.history = []

    def mark_to_market(self, t: int, extra_cost: float = 0.0, target_weights: dict[str, float] | None = None) -> None:
        """Enregistre une ligne d'historique à la date t (mark-to-market) + drift si cible fournie."""
        px = self.prices.iloc[t]
        value = float(sum(self.holdings[a] * px[a] for a in self.assets))

        # Poids courants
        cw = self._current_weights(t)

        # Drift vs cible (optionnel)
        max_drift = None
        l1_drift = None
        if target_weights is not None:
            diffs = [abs(cw.get(a, 0.0) - target_weights.get(a, 0.0)) for a in self.assets]
            if diffs:
                max_drift = float(max(diffs))
                l1_drift = float(sum(diffs))

        rec = {
            "date": self.prices.index[t],
            "value": value,
            "cost": float(extra_cost),
            "weights": None,
            "trades": None,
            "max_drift": max_drift,
            "l1_drift": l1_drift,
        }

        # positions (optionnel)
        for a in self.assets:
            rec[f"pos_{a}"] = float(self.holdings[a])
        self.history.append(rec)

    def _current_weights(self, t: int) -> dict[str, float]:
        px = self.prices.iloc[t]
        total = float(sum(self.holdings[a] * px[a] for a in self.assets))
        if total == 0.0:
            return {a: 0.0 for a in self.assets}
        return {a: (self.holdings[a] * px[a]) / total for a in self.assets}

    def _portfolio_value(self, t: int) -> float:
        px = self.prices.iloc[t]
        return float(sum(self.holdings[a] * px[a] for a in self.assets))

    def rebalance(self, t: int, target_weights: dict[str, float], slippage_map: dict[str, float] = None) -> float:
        total_value = self._portfolio_value(t)
        px = self.prices.iloc[t]
        current_value = {a: self.holdings[a] * px[a] for a in self.assets}
        target_value  = {a: total_value * target_weights.get(a, 0.0) for a in self.assets}

        trade_values_nominal = {a: target_value[a] - current_value[a] for a in self.assets}

        # Calcul des quantités avec slippage
        trades_qty = {}
        slippage_costs = {}  # Coût du slippage par asset
        
        for a in self.assets:
            dv_nominal = trade_values_nominal[a]  # valeur nominale à acheter/vendre (en €)
            p0 = float(px[a])
            
            if p0 == 0 or not np.isfinite(p0):
                trades_qty[a] = 0.0
                slippage_costs[a] = 0.0
                continue

            if abs(dv_nominal) < 1e-12:
                trades_qty[a] = 0.0
                slippage_costs[a] = 0.0
                continue

            # Prix d'exécution avec slippage : achat => prix plus haut, vente => prix plus bas
            slip = slippage_map[a] if slippage_map and a in slippage_map else float(self.trade_cost.slippage)
            if dv_nominal > 0:  # Achat
                p_exec = p0 * (1.0 + slip)
            else:  # Vente
                p_exec = p0 * (1.0 - slip)

            # Quantité achetée/vendue
            qty = dv_nominal / p_exec
            trades_qty[a] = qty
            
            # Coût du slippage : pour un trade de valeur V avec slippage s
            # Le coût est V * s (que ce soit un achat ou une vente)
            # Achat : on paye s% plus cher -> perte de s% de la valeur
            # Vente : on reçoit s% moins -> perte de s% de la valeur
            slippage_costs[a] = abs(dv_nominal) * slip

        # --- Calcul des coûts totaux : frais d'exchange + coût du slippage ---
        # Frais d'exchange (fee_rate sur la valeur du trade)
        cost_fees = self.trade_cost.compute(trade_values_nominal)
        
        # Coût total du slippage (impact de marché)
        cost_slippage = sum(slippage_costs.values())
        
        # Coût total = frais + slippage
        cost = cost_fees + cost_slippage

        # --- applique les trades ---
        for a, q in trades_qty.items():
            self.holdings[a] += q

        # --- paiement des frais : validation et prélèvement intelligent ---
        self._pay_trading_fees(t, cost, px)

        if self.verbose:
            cw = self._current_weights(t)
            drift = {a: cw.get(a, 0) - target_weights.get(a, 0) for a in self.assets}
            actions = []
            for a in self.assets:
                d = drift[a]
                if abs(d) < 0.001:
                    continue
                actions.append(f"{a} {'trop haut' if d>0 else 'trop bas'} ({d*100:.2f}%)")
            trades_summary = []
            for a, q in trades_qty.items():
                if abs(q) < 1e-8:
                    continue
                sign = "Achat" if q > 0 else "Vente"
                trades_summary.append(f"{sign} {a} {abs(q):.6f}")
            print(f"\n[{self.prices.index[t].date()}] Rééquilibrage")
            if actions: print("  Drift : " + "; ".join(actions))
            if trades_summary: print("  " + "; ".join(trades_summary))
            print(f"  Coût total : {cost:.2f} € (frais: {cost_fees:.2f}€ + slippage: {cost_slippage:.2f}€)")

        # ⬅️ on NE pousse plus la ligne d'historique ici : on laisse strategy.py appeler mark_to_market
        return float(cost)

    def get_history(self) -> pd.DataFrame:
        if not self.history:
            return pd.DataFrame(columns=["date", "value", "cost", "weights", "trades"]).set_index("date")
        df = pd.DataFrame(self.history)
        df.set_index("date", inplace=True)
        return df

    def _pay_trading_fees(self, t: int, cost: float, px: pd.Series) -> None:
        """
        Prélève les frais de trading sur le portefeuille avec validation.
        
        Stratégie de prélèvement :
        1. Priorité : USDT si disponible et suffisant
        2. Fallback : Actif avec la plus grande valeur
        3. Si aucun actif n'a assez de valeur : répartition proportionnelle
        4. Si capital total insuffisant : Exception (backtest invalide)
        
        Args:
            t: Index temporel pour logging
            cost: Montant des frais en devise de base (EUR)
            px: Prix à l'instant t (pd.Series)
        """
        if cost <= 0:
            return  # Pas de frais à payer
        
        # Vérifier que le capital total est suffisant
        total_value = self._portfolio_value(t)
        if total_value < cost:
            raise ValueError(
                f"[{self.prices.index[t].date()}] Capital insuffisant pour payer les frais. "
                f"Frais: {cost:.2f}€, Capital: {total_value:.2f}€"
            )
        
        # Stratégie 1 : Prélever sur USDT si présent et suffisant
        pay_asset = "USDT" if "USDT" in self.assets else None
        if pay_asset is not None and px[pay_asset] > 0:
            asset_value = self.holdings[pay_asset] * px[pay_asset]
            if asset_value >= cost:
                # USDT a assez de valeur
                self.holdings[pay_asset] -= cost / px[pay_asset]
                return
        
        # Stratégie 2 : Prélever sur l'actif avec la plus grande valeur
        asset_values = {a: self.holdings[a] * px[a] for a in self.assets if px[a] > 0}
        if asset_values:
            biggest = max(asset_values, key=asset_values.get)
            if asset_values[biggest] >= cost:
                # L'actif le plus gros a assez de valeur
                self.holdings[biggest] -= cost / px[biggest]
                return
        
        # Stratégie 3 : Répartition proportionnelle sur tous les actifs
        # (aucun actif individuel n'a assez, mais le total oui)
        for asset in self.assets:
            if px[asset] > 0 and self.holdings[asset] > 0:
                asset_value = self.holdings[asset] * px[asset]
                # Prélever proportionnellement à la valeur de l'actif
                fee_share = (asset_value / total_value) * cost
                self.holdings[asset] -= fee_share / px[asset]
        
        # Validation finale : vérifier qu'aucun holding n'est devenu négatif
        for asset in self.assets:
            if self.holdings[asset] < -1e-10:  # Tolérance pour erreurs d'arrondi
                if self.verbose:
                    print(f"⚠️ Warning: Holding négatif détecté pour {asset}: {self.holdings[asset]:.8f}")
                self.holdings[asset] = 0.0  # Correction pour éviter holdings négatifs
