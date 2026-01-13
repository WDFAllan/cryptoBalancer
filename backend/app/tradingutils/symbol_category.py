# Utilitaire pour catégoriser les crypto-paires/trades selon la liquidité
# Usage universel pour les stratégies/runners

def get_symbol_category(symbol: str) -> str:
    """
    Retourne la catégorie de liquidité de la paire/symbole ("majors", "high_liq", "others").
    Personnalise les règles ci-dessous selon tes logiques métiers !
    """
    majors = {"BTC", "ETH"}
    high_liq = {"BNB", "SOL", "XRP"}  # À étendre selon ta connaissance du marché
    base = symbol[:3].upper() if len(symbol) >= 3 else symbol.upper()
    if base in majors:
        return "majors"
    if base in high_liq:
        return "high_liq"
    return "others"

