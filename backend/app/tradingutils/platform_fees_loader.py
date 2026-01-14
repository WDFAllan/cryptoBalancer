import json
import os

PLATFORM_FEES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "core", "platform_fees.json")

# Singleton cache pour ne lire le fichier qu'une seule fois
_platform_fees_cache = None

def load_platform_fees():
    global _platform_fees_cache
    if _platform_fees_cache is None:
        with open(PLATFORM_FEES_PATH, "r", encoding="utf-8") as f:
            _platform_fees_cache = json.load(f)
    return _platform_fees_cache


def get_fees_for_platform(platform_name: str):
    fees_data = load_platform_fees()
    return fees_data.get(platform_name)


def get_fee_rate(platform_name: str) -> float:
    platform = get_fees_for_platform(platform_name)
    if platform:
        return platform.get("fee", 0.0)
    return 0.0


def get_slippage_rate(platform_name: str, category: str) -> float:
    platform = get_fees_for_platform(platform_name)
    if platform:
        return platform.get("slippage", {}).get(category, 0.0)
    return 0.0

