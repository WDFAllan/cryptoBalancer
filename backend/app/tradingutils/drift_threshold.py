# Utilitaire pour le drift threshold dynamique/finement configurable
from app.tradingutils.symbol_category import get_symbol_category

# Seuils par catégorie par défaut
CATEGORY_DEFAULTS = {
    "majors": 0.03,    # 3%
    "high_liq": 0.02,  # 2%
    "others": 0.01     # 1%
}

# (optionnel) Personnalisation plateforme
PLATFORM_OVERRIDES = {
    # "Binance": {"majors": 0.025, ...}
}

def get_drift_threshold(symbol: str, platform: str = None) -> float:
    """
    Donne le threshold de drift (en valeur absolue, e.g. 0.01 pour 1%) selon l'asset
    Peut être enrichi pour prendre en compte plus d'infos (liquidité, volatilité, etc)
    """
    cat = get_symbol_category(symbol)
    # Si plateforme a des overrides, on prend sa config
    if platform in PLATFORM_OVERRIDES:
        override = PLATFORM_OVERRIDES[platform]
        if cat in override:
            return override[cat]
    # Sinon fallback sur la logique générale
    return CATEGORY_DEFAULTS.get(cat, 0.01)

