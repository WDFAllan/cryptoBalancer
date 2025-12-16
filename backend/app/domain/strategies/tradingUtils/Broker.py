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

    def rebalance(self, t: int, target_weights: dict[str, float]) -> float:
        total_value = self._portfolio_value(t)
        px = self.prices.iloc[t]
        current_value = {a: self.holdings[a] * px[a] for a in self.assets}
        target_value  = {a: total_value * target_weights.get(a, 0.0) for a in self.assets}

        trade_values = {a: target_value[a] - current_value[a] for a in self.assets}
        # --- frais (calculés sur la valeur nominale, hors slippage) ---
        cost = self.trade_cost.compute(trade_values)

        # --- exécution avec slippage directionnel sur le prix d'exécution ---
        slip = float(self.trade_cost.slippage)
        trades_qty = {}
        for a in self.assets:
            dv = trade_values[a]  # valeur à acheter/vendre (en €)
            p0 = float(px[a])
            if p0 == 0 or not np.isfinite(p0):
                trades_qty[a] = 0.0
                continue

            if abs(dv) < 1e-12:
                trades_qty[a] = 0.0
                continue

            # Prix d'exécution avec slippage : achat => prix plus haut, vente => prix plus bas
            if dv > 0:  # Achat
                p_exec = p0 * (1.0 + slip)
            else:  # Vente
                p_exec = p0 * (1.0 - slip)

            qty = dv / p_exec
            trades_qty[a] = qty

        # --- applique les trades ---
        for a, q in trades_qty.items():
            self.holdings[a] += q

        # --- paiement des frais : on les prélève sur un stable (USDT si présent)
        pay_asset = "USDT" if "USDT" in self.assets else None
        if pay_asset is not None and px[pay_asset] > 0:
            self.holdings[pay_asset] -= cost / px[pay_asset]
        else:
            # fallback minimaliste : on prélève sur l’actif de plus grande valeur
            # (évite la disparition des frais)
            biggest = max(self.assets, key=lambda a: self.holdings[a] * px[a])
            if px[biggest] > 0:
                self.holdings[biggest] -= cost / px[biggest]

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
            print(f"  Coût total frais : {cost:.2f} €")

        # ⬅️ on NE pousse plus la ligne d'historique ici : on laisse strategy.py appeler mark_to_market
        return float(cost)

    def get_history(self) -> pd.DataFrame:
        if not self.history:
            return pd.DataFrame(columns=["date", "value", "cost", "weights", "trades"]).set_index("date")
        df = pd.DataFrame(self.history)
        df.set_index("date", inplace=True)
        return df
