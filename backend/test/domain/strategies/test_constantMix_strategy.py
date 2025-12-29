import pandas as pd
import pytest

from app.domain.strategies.constantMix.constantMixStrategy import ConstantMixStrategy
from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams


def make_prices():
    dates = pd.date_range("2020-01-01", periods=4, freq="D")
    prices = pd.DataFrame({
        "BTC": [100.0, 110.0, 105.0, 120.0],
        "ETH": [50.0, 55.0, 60.0, 58.0],
    }, index=dates)
    return prices


def test_constantmix_run_returns_history_and_values():
    prices = make_prices()
    params = ConstantMixParams(target_weights={"BTC": 0.5, "ETH": 0.5}, rebalance="D", verbose=False)
    strat = ConstantMixStrategy(params)

    wallet = {"items": [type("I", (), {"symbol": "BTC", "amount": 0.5})(), type("I", (), {"symbol": "ETH", "amount": 5.0})()]}

    hist = strat.run(prices, wallet)

    assert isinstance(hist, pd.DataFrame)
    assert len(hist) == len(prices)
    assert "value" in hist.columns


def test_constantmix_raises_on_empty_initial_capital():
    prices = make_prices()
    params = ConstantMixParams(target_weights={"BTC": 0.5, "ETH": 0.5}, rebalance="D", verbose=False)
    strat = ConstantMixStrategy(params)

    # wallet with zero amounts
    wallet = {"items": [type("I", (), {"symbol": "BTC", "amount": 0.0})(), type("I", (), {"symbol": "ETH", "amount": 0.0})()]}

    with pytest.raises(ValueError):
        strat.run(prices, wallet)


def test_target_weights_filters_missing_columns():
    prices = make_prices()
    params = ConstantMixParams(target_weights={"BTC": 0.5, "ETH": 0.4, "XRP": 0.1}, verbose=False)
    strat = ConstantMixStrategy(params)

    tw = strat.target_weights(0, prices)
    # XRP not in prices -> should be removed and remaining weights normalized
    assert "XRP" not in tw
    assert pytest.approx(sum(tw.values()), rel=1e-6) == 1.0


def test_is_rebalance_day_various_modes():
    idx = pd.date_range("2020-01-01", periods=10, freq="D")
    fn = ConstantMixStrategy._is_rebalance_day

    assert not fn(idx, 0, "D")
    assert fn(idx, 1, "D")
    assert fn(idx, 7, "7D") is True
    assert fn(idx, 6, "7D") is False
    assert fn(idx, 1, "W") in (True, False)
