from datetime import datetime
from typing import List

from app.domain.models.portfolioValue import PortfolioValue
from app.domain.port.portfolioValuePort import IPortfolioValuePort
from app.domain.port.walletPort import IWalletPort
from app.domain.services.cryptoService import CryptoService


class PortfolioValueService:

    def __init__(self, portfolioValueRepo: IPortfolioValuePort, walletRepo: IWalletPort, cryptoService: CryptoService):
        self.portfolioValueRepo = portfolioValueRepo
        self.walletRepo = walletRepo
        self.cryptoService = cryptoService

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

