# balancing_bot/core/utils.py
import os
import numpy as np
import pandas as pd

# ----------- Math & statistiques -----------

def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    """Renvoie un dict dont la somme des poids vaut 1 (tolérance flottante)."""
    total = float(sum(weights.values()))
    if abs(total) < 1e-12:
        return {k: 0.0 for k in weights}
    return {k: float(v) / total for k, v in weights.items()}



def zscore(series: pd.Series, window: int = 20) -> pd.Series:
    """Z-score glissant : (x - mean)/std."""
    mean = series.rolling(window).mean()
    std = series.rolling(window).std()
    return (series - mean) / std


def moving_volatility(series: pd.Series, window: int = 30, periods_per_year: int = 365) -> pd.Series:
    """Volatilité annualisée glissante (log-returns)."""
    log_ret = np.log(series).diff()  # plus robuste que series/shift
    vol = log_ret.rolling(window, min_periods=window).std() * np.sqrt(periods_per_year)
    return vol


def drawdown_curve(prices: pd.Series) -> pd.Series:
    """Courbe du drawdown (en %) à partir d'une série de prix ou valeur portefeuille."""
    peak = prices.cummax()
    dd = (prices / peak) - 1.0
    return dd


def max_drawdown(prices: pd.Series) -> float:
    """Retourne le drawdown maximum (valeur positive)."""
    return -drawdown_curve(prices).min()


# ----------- Performance -----------

def compute_cagr(series, *, use_index=True, periods_per_year=365):
    """
    CAGR annualisé.
    - use_index=True : calcule la durée avec les dates de l'index (recommandé)
    - use_index=False : annualise via 'periods_per_year' (si index non temporel)
    """
    if len(series) < 2:
        return 0.0
    v0, vf = float(series.iloc[0]), float(series.iloc[-1])
    if not np.isfinite(v0) or not np.isfinite(vf) or v0 <= 0.0 or vf <= 0.0:
        return 0.0


    if use_index:
        idx = series.index
        # sécurité : tenter conversion datetime si nécessaire
        try:
            start, end = pd.to_datetime(idx[0]), pd.to_datetime(idx[-1])
        except Exception:
            use_index = False

    if use_index:
        days = (end - start).days
        if days <= 0:
            return 0.0
        n_years = days / 365.25
        return (vf / v0) ** (1.0 / n_years) - 1.0
    else:
        n_years = len(series) / periods_per_year
        if n_years <= 0:
            return 0.0
        return (vf / v0) ** (1.0 / n_years) - 1.0



def sharpe_ratio(series: pd.Series, rf: float = 0.0, periods_per_year: int = 365) -> float:
    """Sharpe ratio annualisé (log-returns)."""
    rets = np.log(series).diff().dropna()
    excess = rets - (rf / periods_per_year)
    std = excess.std()
    if std == 0 or not np.isfinite(std):
        return 0.0
    return np.sqrt(periods_per_year) * excess.mean() / std



# ----------- Divers -----------

def pct_format(x: float, digits: int = 2) -> str:
    """Formate un nombre en pourcentage proprement."""
    return f"{x * 100:.{digits}f}%"