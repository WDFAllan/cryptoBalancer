from unittest.mock import Mock, patch

import pytest

from app.domain.services.backtestService import BacktestService

def test_run_strategy_executes_runner_with_prices_and_wallet():
    dailyCandleRepo = Mock()
    wallet_service = Mock()

    candle = Mock(
        open_time="2025-12-1",
        open=100,
        high=110,
        low=90,
        close=105,
        symbol="BTC"
    )

    dailyCandleRepo.getAllCandles.return_value = [candle]

    wallet = Mock()
    wallet_service.getWalletByUserId.return_value = wallet

    runner = Mock()
    runner.run.return_value = "RESULT"

    runnerCls = Mock(return_value=runner)

    with patch("app.domain.services.backtestService.StrategyFactory.create",
               return_value=runnerCls
    ):
        service = BacktestService(
            dailyCandleRepo=dailyCandleRepo,
            walletService=wallet_service
        )

        result = service.runStrategy("constant_mix",userId=42)

    assert result == "RESULT"

    dailyCandleRepo.getAllCandles.assert_called_once()
    wallet_service.getWalletByUserId.assert_called_once_with(42)

    runnerCls.assert_called_once()
    runner.run.assert_called_once()

    pricesDf,passedWallet = runner.run.call_args[0]

    assert passedWallet == wallet
    assert not pricesDf.empty

def test_run_strategy_raises_if_strategy_not_found():
    daily_candle_repo = Mock()
    wallet_service = Mock()

    candle = Mock(
        open_time="2024-01-01",
        open=100,
        high=110,
        low=90,
        close=105,
        symbol="BTC"
    )

    daily_candle_repo.getAllCandles.return_value = [candle]

    with patch(
        "app.domain.services.backtestService.StrategyFactory.create",
        side_effect=ValueError("Unknown strategy")
    ):
        service = BacktestService(dailyCandleRepo=daily_candle_repo, walletService=wallet_service)

        with pytest.raises(ValueError):
            service.runStrategy("unknown", userId=1)
