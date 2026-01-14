import pandas as pd
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.port.candlePort import ICandlePort
from app.domain.port.walletPort import IWalletPort
from app.domain.services import walletService
from app.domain.services.walletService import WalletService
from app.domain.strategies.constantMix.constantMixParams import ConstantMixParams
from app.infrastructure.repository import walletRepository
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.repository.walletRepository import WalletRepository
from app.infrastructure.repository.userRepository import UserRepository
from app.infrastructure.runners.StrategyFactory import StrategyFactory
from app.tradingutils.platform_fees_loader import get_fee_rate, get_slippage_rate

class BacktestService:
    def __init__(self, dailyCandleRepo: dailyCandleRepository, walletService: WalletService, userRepo: UserRepository):
        self.dailyCandleRepository = dailyCandleRepo
        self.walletService = walletService
        self.userRepo = userRepo

    def runStrategy(self, strategy_name: str, userId: int, params=None):
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
        wallet = self.walletService.getWalletByUserId(userId)

        user = self.userRepo.get_by_id(userId)
        favorite_platform = user.favorite_platform if user else "Binance"
        fee_rate = get_fee_rate(favorite_platform)
        # Le slippage sera calculé par asset dans chaque stratégie selon la catégorie
        # On garde un slippage de fallback pour compatibilité mais il sera ignoré par les stratégies modernes
        slippage_rate = get_slippage_rate(favorite_platform, "majors")  # Fallback si stratégie ne supporte pas slippage_map

        runner_cls = StrategyFactory.create(strategy_name)
        runner = runner_cls()
        return runner.run(prices_df, wallet, fee_rate=fee_rate, slippage=slippage_rate, favorite_platform=favorite_platform)
