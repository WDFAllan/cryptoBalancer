from datetime import timedelta, timezone, datetime


class baseCandleService:

    def __init__(self, candleRepo, cryptoRepo, binanceAdapter, timeframe: str, retention_days: int):
        self.candleRepo = candleRepo
        self.cryptoRepo = cryptoRepo
        self.binanceAdapter = binanceAdapter
        self.timeframe = timeframe
        self.retention_days = retention_days

    async def syncPeriod(self, period_days: int):
        symbols = await self.cryptoRepo.get_all_symbols()

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=period_days)

        for sym in symbols:
            print(sym)
            candles = self.binanceAdapter.fetchCandles(sym, start, end, self.timeframe)
            print(candles)
            await self.candleRepo.saveCandles(sym, candles)

    async def updateCandles(self):
        symbols = await self.cryptoRepo.get_all_symbols()

        now=0
        if self.timeframe.endswith("m"):
            now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        if self.timeframe.endswith("d"):
            now = datetime.now(timezone.utc).replace(minute=0,second=0, microsecond=0)

        start = now - self._timeframe_to_delta()

        for sym in symbols:
            try:
                candles = self.binanceAdapter.fetchCandles(sym, start, now, self.timeframe)

                if not candles:
                    continue

                await self.candleRepo.saveCandles(sym, candles)
                await self.candleRepo.deleteOlderThan(sym, now - timedelta(days=self.retention_days))

            except Exception:
                continue

    def _timeframe_to_delta(self):
        if self.timeframe.endswith("d"):
            return timedelta(days=int(self.timeframe[:-1]))
        if self.timeframe.endswith("m"):
            return timedelta(minutes=int(self.timeframe[:-1]))
        raise ValueError("Timeframe non supporté")
