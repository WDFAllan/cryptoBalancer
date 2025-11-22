import requests
from datetime import datetime

class binanceCandleAdapter:

    BASE_URL = "https://api.binance.com/api/v3/klines"

    def fetchDailyCandles(self, symbol: str, start: datetime, end: datetime):

        all_candles = []

        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)

        while True:

            params = {
                "symbol": symbol.upper(),
                "interval": "1d",
                "startTime": start_ms,
                "endTime": end_ms,
                "limit": 1000
            }

            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            if not data:
                break

            # Ajout
            for c in data:
                all_candles.append({
                    "open_time": datetime.fromtimestamp(c[0] / 1000),
                    "open": float(c[1]),
                    "high": float(c[2]),
                    "low": float(c[3]),
                    "close": float(c[4])
                })
            # Dernière bougie renvoyée
            last_ts = data[-1][0]

            # Si Binance nous a renvoyé TOUT ce qui existe
            if last_ts >= end_ms:
                break

            # Avancer au lendemain pour éviter le doublon
            start_ms = last_ts + 24 * 3600 * 1000

            # Sécurité anti boucle infinie
            if start_ms > end_ms:
                break

        return all_candles