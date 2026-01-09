from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem
from app.domain.port.walletPort import IWalletPort


class WalletService:

    def __init__(self, walletRepo:IWalletPort):
        self.walletRepo = walletRepo

    def createWalletForUser(self, user_id: int) -> Wallet:
        if user_id <= 0:
            raise ValueError("user_id must be > 0")

        existing_wallet = self.walletRepo.getWalletByUserId(user_id)
        if existing_wallet:
            raise Exception(f"User {user_id} already has a wallet.")
        return self.walletRepo.createWallet(user_id)


    def addItemToWallet(self, user_id: int, symbol: str, amount: float) -> Wallet:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        item = WalletItem(id=None ,symbol=symbol, amount=amount)
        return self.walletRepo.addToWallet(user_id, item)


    def getWalletByUserId(self, user_id: int) -> Wallet:
        return self.walletRepo.getWalletByUserId(user_id)

    def walletExists(self, user_id: int) -> bool:
        wallet = self.walletRepo.getWalletByUserId(user_id)
        return wallet is not None

    def deleteWallet(self, user_id: int) -> None:
        wallet = self.walletRepo.getWalletByUserId(user_id)
        if not wallet:
            raise Exception(f"No wallet found for user {user_id}")
        self.walletRepo.deleteWallet(user_id)

    def removeItemFromWallet(self, user_id: int, symbol: str) -> Wallet:
        if not symbol or symbol.strip() == "":
            raise ValueError("symbol cannot be empty")
        return self.walletRepo.removeItemFromWallet(user_id, symbol)

    def updateItemAmount(self, user_id: int, symbol: str, amount: float) -> Wallet:
        if not symbol or symbol.strip() == "":
            raise ValueError("symbol cannot be empty")
        if amount < 0:
            raise ValueError("amount must be >= 0")
        return self.walletRepo.updateItemAmount(user_id, symbol, amount)
