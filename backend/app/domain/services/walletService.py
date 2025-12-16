from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem
from app.domain.port.walletPort import IWalletPort


class WalletService:

    def __init__(self, walletRepo:IWalletPort):
        self.walletRepo = walletRepo

    def createWalletForUser(self, user_id: int) -> Wallet:
        existing_wallet = self.walletRepo.getWalletByUserId(user_id)
        if existing_wallet:
            raise Exception(f"User {user_id} already has a wallet.")
        return self.walletRepo.createWallet(user_id)


    def addItemToWallet(self, user_id: int, symbol: str, amount: float) -> Wallet:
        item = WalletItem(id=None ,symbol=symbol, amount=amount)
        return self.walletRepo.addToWallet(user_id, item)


    def getWalletByUserId(self, user_id: int) -> Wallet:
        return self.walletRepo.getWalletByUserId(user_id)
