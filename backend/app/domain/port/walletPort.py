from abc import ABC, abstractmethod

from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem


class IWalletPort(ABC):

    @abstractmethod
    def createWallet(self,userId:int) -> Wallet:
        pass

    @abstractmethod
    def addToWallet(self,userId: int,walletItem: WalletItem):
        pass

    @abstractmethod
    def getWalletByUserId(self,userId:int) -> Wallet:
        pass

    @abstractmethod
    def deleteWallet(self, userId: int) -> None:
        pass
