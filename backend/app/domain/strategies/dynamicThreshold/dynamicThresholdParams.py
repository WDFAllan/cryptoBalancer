from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class DynamicThresholdParams:
    target_weights: Dict[str, float] = None
    initial_capital: float = 10000.0
    fee_rate: float = 0.001
    fixed_fee: float = 1.0
    slippage: float = 0.0002
    verbose: bool = False
    
    # Paramètres de volatilité
    vol_window: int = 40  # Fenêtre pour calculer la volatilité (jours)
    k: float = 0.20  # Facteur pour ajuster le seuil selon la volatilité
    
    # Paramètres du seuil dynamique
    min_th: float = 0.03  # Seuil minimum (3%)
    max_th: float = 0.20  # Seuil maximum (20%)
    
    # Paramètres pour actifs stables
    stable_assets: Tuple[str, ...] = ("USDT",)  # Actifs stables avec seuil différent
    stable_threshold: float = 0.005  # Seuil pour les actifs stables (0.5%)
    
    # Paramètres de rééquilibrage
    rebal_frac: float = 1.0  # Fraction de rééquilibrage (1.0 = complet, < 1.0 = partiel)
    cooldown_days: int = 5  # Délai minimum entre deux rééquilibrages (jours)

