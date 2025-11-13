from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.models.wallet.wallet import Wallet
from app.domain.models.wallet.walletItem import WalletItem
from app.domain.services.walletService import WalletService
from app.infrastructure.repository.walletRepository import WalletRepository

router = APIRouter(prefix="/wallet", tags=["Wallet"])

def wallet_service(db:Session = Depends(get_db)) -> WalletService:
    return WalletService(WalletRepository(db))


@router.post("/{userId}/create", response_model=Wallet)
def createWallet(userId: int, service: WalletService = Depends(wallet_service)):
    try:
        return service.createWalletForUser(userId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getWalletByUserId/{userId}", response_model=Wallet)
def getWalletByUserId(user_id: int, service: WalletService = Depends(wallet_service)):
    try:
        return service.getWalletByUserId(user_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{userId}/addItemToWalletByUserID", response_model=Wallet)
def addItemToWallet(userId: int, symbol: str, amount: float,service:WalletService = Depends(wallet_service)):
    try:
        return service.addItemToWallet(userId, symbol, amount)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

