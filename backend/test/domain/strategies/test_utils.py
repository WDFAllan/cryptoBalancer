import pandas as pd
import pytest

from app.domain.strategies.tradingUtils.Utils import (
    normalize_weights,
    wallet_items_to_holdings,
    compute_portfolio_value,
)


def test_normalize_weights_zero_total():
    w = {"A": 0.0, "B": 0.0}
    nw = normalize_weights(w)
    assert nw["A"] == 0.0 and nw["B"] == 0.0


def test_wallet_items_to_holdings_with_dict_and_object():
    wallet_dict = {"items": [type("Item", (), {"symbol": "BTC", "amount": 1.0})()]}
    h = wallet_items_to_holdings(wallet_dict)
    assert h == {"BTC": 1.0}


def test_compute_portfolio_value_ignores_missing_assets():
    holdings = {"BTC": 1.0, "XRP": 2.0}
    prices = pd.Series({"BTC": 100.0})
    value = compute_portfolio_value(holdings, prices)
    assert value == 100.0  # XRP missing -> ignored
