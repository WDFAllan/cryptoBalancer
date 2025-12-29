import pandas as pd

from app.domain.strategies.hold.holdStrategy import holdStrategy


def test_hold_strategy_computes_portfolio_value():
    dates = pd.date_range("2020-01-01", periods=3)
    prices = pd.DataFrame({"BTC": [100.0, 110.0, 105.0], "ETH": [50.0, 55.0, 60.0]}, index=dates)

    wallet = {"items": [type("I", (), {"symbol": "BTC", "amount": 1.0})(), type("I", (), {"symbol": "ETH", "amount": 2.0})()]}

    s = holdStrategy()
    df = s.run(prices, wallet)

    # expected values: BTC*1 + ETH*2
    expected = prices["BTC"] * 1.0 + prices["ETH"] * 2.0
    pd.testing.assert_series_equal(df["value"], expected, check_names=False)
