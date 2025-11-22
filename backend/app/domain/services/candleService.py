from datetime import datetime, timedelta, timezone

from app.domain.port.candlePort import ICandlePort
from app.domain.port.cryptoPort import ICryptoPort


class CandleService:

    def __init__(self, candleRepo:ICandlePort, cryptoRepo:ICryptoPort, binanceCandleAdapter):
        self.candleRepo = candleRepo
        self.cryptoRepo = cryptoRepo
        self.binanceCandleAdapter = binanceCandleAdapter  # Binance adapter

    async def syncLastTwoYears(self):

        symbols = await self.cryptoRepo.get_all_symbols()
        print("symbols:", len(symbols),symbols)

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=730)

        for sym in symbols:

            candles = self.binanceCandleAdapter.fetchDailyCandles(sym, start, end)
            try:
                await self.candleRepo.saveCandles(sym, candles)
            except Exception as e:
                print("ERREUR SQL :",e)
                raise

    def getCandles(self, symbol: str):
        return self.candleRepo.getCandlesBySymbol(symbol)