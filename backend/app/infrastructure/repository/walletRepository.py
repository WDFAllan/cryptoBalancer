from sqlalchemy.orm import Session
from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem
from app.domain.port.walletPort import IWalletPort
from app.infrastructure.models.wallet.walletItemTable import WalletItemTable
from app.infrastructure.models.wallet.walletTable import WalletTable


class WalletRepository(IWalletPort):

    def __init__(self, db: Session):
        self.db = db

    def createWallet(self, userId: int) -> Wallet:

        wallet_table = WalletTable(userId=userId)
        self.db.add(wallet_table)
        self.db.commit()
        self.db.refresh(wallet_table)

        return Wallet(id=None,userId=userId, items=[])

    def addToWallet(self, userId: int, walletItem: WalletItem):
        wallet_table = (
            self.db.query(WalletTable)
            .filter_by(userId = userId)
            .first()
        )

        if not wallet_table:
            raise Exception(f"No wallet found for user {userId}")

        # Vérifie si l’item existe déjà (même symbole)
        existing_item = next(
            (i for i in wallet_table.items if i.symbol == walletItem.symbol),
            None
        )

        if existing_item:
            existing_item.amount += walletItem.amount
        else:
            new_item = WalletItemTable(
                walletId=wallet_table.id,
                symbol=walletItem.symbol,
                amount=walletItem.amount
            )
            self.db.add(new_item)

        self.db.commit()
        self.db.refresh(wallet_table)

        # Convertir vers le modèle domaine
        items = [
            WalletItem(id=i.id, symbol=i.symbol, amount=i.amount)
            for i in wallet_table.items
        ]
        return Wallet(id=None,userId=wallet_table.userId, items=items)



    def getWalletByUserId(self,userId:int) -> Wallet:
        wallet_table = (
            self.db.query(WalletTable)
            .filter(WalletTable.userId == userId)
            .first()
        )
        if not wallet_table:
            return None

        items = [
            WalletItem(id=i.id, symbol=i.symbol, amount=i.amount)
            for i in wallet_table.items
        ]

        return Wallet(id=None,userId=userId, items=items)

    def deleteWallet(self, userId: int) -> None:
        wallet_table = (
            self.db.query(WalletTable)
            .filter(WalletTable.userId == userId)
            .first()
        )

        if not wallet_table:
            raise Exception(f"No wallet found for user {userId}")

        # Grâce au cascade="all, delete-orphan", les WalletItems seront supprimés automatiquement
        self.db.delete(wallet_table)
        self.db.commit()

    def removeItemFromWallet(self, userId: int, symbol: str) -> Wallet:
        wallet_table = (
            self.db.query(WalletTable)
            .filter(WalletTable.userId == userId)
            .first()
        )

        if not wallet_table:
            raise Exception(f"No wallet found for user {userId}")

        # Chercher l'item avec le symbole spécifié
        item_to_remove = next(
            (i for i in wallet_table.items if i.symbol == symbol),
            None
        )

        if not item_to_remove:
            raise Exception(f"No item with symbol {symbol} found in wallet")

        # Supprimer l'item
        self.db.delete(item_to_remove)
        self.db.commit()
        self.db.refresh(wallet_table)

        # Convertir vers le modèle domaine
        items = [
            WalletItem(id=i.id, symbol=i.symbol, amount=i.amount)
            for i in wallet_table.items
        ]
        return Wallet(id=None, userId=wallet_table.userId, items=items)

    def updateItemAmount(self, userId: int, symbol: str, amount: float) -> Wallet:
        wallet_table = (
            self.db.query(WalletTable)
            .filter(WalletTable.userId == userId)
            .first()
        )

        if not wallet_table:
            raise Exception(f"No wallet found for user {userId}")

        # Chercher l'item avec le symbole spécifié
        item_to_update = next(
            (i for i in wallet_table.items if i.symbol == symbol),
            None
        )

        if not item_to_update:
            raise Exception(f"No item with symbol {symbol} found in wallet")

        # Mettre à jour la quantité
        item_to_update.amount = amount
        self.db.commit()
        self.db.refresh(wallet_table)

        # Convertir vers le modèle domaine
        items = [
            WalletItem(id=i.id, symbol=i.symbol, amount=i.amount)
            for i in wallet_table.items
        ]
        return Wallet(id=None, userId=wallet_table.userId, items=items)