from datetime import datetime, timedelta, timezone
from typing import List

from app.domain.models.portfolioValue import PortfolioValue
from app.domain.port.portfolioValuePort import IPortfolioValuePort
from app.domain.port.walletPort import IWalletPort
from app.domain.services.cryptoService import CryptoService
from app.domain.services.candle.dailyCandleService import dailyCandleService



class PortfolioValueService:

    def __init__(self, portfolioValueRepo: IPortfolioValuePort, walletRepo: IWalletPort, cryptoService: CryptoService, candleService: dailyCandleService):
        self.portfolioValueRepo = portfolioValueRepo
        self.walletRepo = walletRepo
        self.cryptoService = cryptoService
        self.candleService = candleService

    async def calculateAndSavePortfolioValue(self, userId: int, date: datetime | None = None) -> PortfolioValue:
        """
        Calcule la valeur totale du portefeuille de l'utilisateur et la sauvegarde.
        Si aucune date n'est fournie, utilise la date actuelle.
        """
        if date is None:
            date = datetime.now()

        if self.portfolioValueRepo.getByUserIdAndDateRange(userId,date,date) is not None:
            raise Exception(f"Portfolio value already exists for user {userId} and date {date}")

        # Récupérer le wallet de l'utilisateur
        wallet = self.walletRepo.getWalletByUserId(userId)
        if not wallet:
            raise Exception(f"No wallet found for user {userId}")

        # Calculer la valeur totale
        totalValue = 0.0
        for item in wallet.items:
            # Récupérer le prix actuel de la crypto
            price = await self.cryptoService.get_crypto_price(item.symbol)
            totalValue += item.amount * price

        # Sauvegarder la valeur
        return self.portfolioValueRepo.create(userId, date, totalValue)

    def getPortfolioValueHistory(self, userId: int) -> List[PortfolioValue]:
        """
        Récupère tout l'historique des valeurs du portefeuille pour un utilisateur.
        """
        return self.portfolioValueRepo.getByUserId(userId)

    def getPortfolioValueByDateRange(self, userId: int, startDate: datetime, endDate: datetime) -> List[PortfolioValue]:
        """
        Récupère l'historique des valeurs du portefeuille pour une période donnée.
        """
        return self.portfolioValueRepo.getByUserIdAndDateRange(userId, startDate, endDate)

    def getLatestPortfolioValue(self, userId: int) -> PortfolioValue | None:
        """
        Récupère la dernière valeur sauvegardée du portefeuille.
        """
        return self.portfolioValueRepo.getLatestByUserId(userId)

    async def calculateDailyPortfolioValue(self, userId: int) -> List[PortfolioValue]:

        wallet = self.walletRepo.getWalletByUserId(userId)
        if not wallet:
            raise Exception(f"No wallet found for user {userId}")

        startDate = datetime.now(timezone.utc) - timedelta(days=729)
        endDate = datetime.now(timezone.utc)

        # 1️⃣ Charger toutes les candles par crypto
        candles_by_crypto: Dict[str, Dict[datetime, float]] = {}

        for item in wallet.items:
            candles = self.candleService.getCandlesBySymbol(item.symbol)

            # dict[date -> close]
            candles_by_crypto[item.symbol] = {
                candle.open_time.date(): candle.close
                for candle in candles
            }
        
        # 2️⃣ Calcul jour par jour
        dailyValues: List[PortfolioValue] = []
        currentDate = startDate.date()
        endDateOnly = endDate.date()

        while currentDate <= endDateOnly:
            totalValue = 0.0
            for item in wallet.items:
                
                price = candles_by_crypto[item.symbol].get(currentDate)
                
                if price is not None:
                    totalValue += item.amount * price

            dailyValues.append(
                PortfolioValue(
                    id=None,
                    userId=userId,
                    date=datetime.combine(currentDate, datetime.min.time(), tzinfo=timezone.utc),
                    totalValue=totalValue
                )
            )

            currentDate += timedelta(days=1)

        return dailyValues
