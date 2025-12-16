import pandas as pd
from app.domain.port.candlePort import ICandlePort
from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.runners.StrategyFactory import StrategyFactory


class BacktestService:

    def __init__(self, dailyCandleRepo: dailyCandleRepository):
        self.dailyCandleRepository = dailyCandleRepo

    def runStrategy(self, strategy_name: str,params=None):
        candles = self.dailyCandleRepository.getAllCandles()

        candles_list = [
            {
                "open_time": c.open_time,
                "close": c.close,
                "high": c.high,
                "low": c.low,
                "open": c.open,
                "symbol": c.symbol,
            }
            for c in candles
        ]

        df = pd.DataFrame(candles_list)
        df['open_time'] = pd.to_datetime(df['open_time'])
        df.set_index('open_time', inplace=True)
        prices_df = df.pivot(columns='symbol', values='close')

        runner_cls = StrategyFactory.create(strategy_name)  # renvoie la classe runner
        runner = runner_cls()  # instancie le runner avec ses paramètres fixes

        # 3) Exécute le backtest
        return runner.run(prices_df)

