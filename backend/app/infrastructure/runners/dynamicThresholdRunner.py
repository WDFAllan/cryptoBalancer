import pandas as pd
from typing import Dict

from app.domain.strategies.dynamicThreshold.dynamicThresholdParams import DynamicThresholdParams
from app.domain.strategies.dynamicThreshold.dynamicThresholdStrategy import DynamicThresholdStrategy


class DynamicThresholdRunner:

    def run(self, prices: pd.DataFrame, wallet: dict, fee_rate: float = 0.001, slippage: float = 0.0002, favorite_platform: str = "Binance"):
        """
        Lance le backtest avec la stratégie DynamicThreshold.
        
        Args:
            prices: DataFrame des prix historiques
            wallet: Wallet de l'utilisateur
            fee_rate: Taux de frais (défaut: 0.001 = 0.1%)
            slippage: Slippage moyen (défaut: 0.0002 = 0.02%)
            favorite_platform: Plateforme pour calculer slippage par asset (défaut: "Binance")
        """
        # Note: Les symboles doivent correspondre aux colonnes du DataFrame prices
        # Format attendu: "BTCEUR", "ETHEUR", etc. (ou "BTC", "ETH" selon votre format)
        params = DynamicThresholdParams(
            target_weights={"BTCEUR": 0.70, "ETHEUR": 0.20, "BNBEUR": 0.0, "XRPEUR": 0.10, "USDTEUR": 0.0},
            vol_window=40,
            k=0.20,  # Facteur d'ajustement selon volatilité (essayer 0.15 / 0.20 / 0.25)
            min_th=0.03,  # Seuil minimum (3%)
            max_th=0.20,  # Seuil maximum (20%)
            stable_assets=("USDTEUR",),  # Actifs stables avec seuil différent
            stable_threshold=0.005,  # Seuil pour actifs stables (0.5%)
            rebal_frac=1.0,  # Rééquilibrage complet (1.0 = 100%)
            cooldown_days=5,  # Délai minimum entre rééquilibrages (essayer 0 / 5 / 10)
            initial_capital=10_000.0,
            fee_rate=fee_rate,
            fixed_fee=1.0,
            slippage=slippage,
            verbose=False,
            favorite_platform=favorite_platform
        )
        strategy = DynamicThresholdStrategy(params)
        return strategy.run(prices, wallet)

