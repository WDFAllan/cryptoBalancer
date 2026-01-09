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
def getWalletByUserId(userId: int, service: WalletService = Depends(wallet_service)):
    try:
        return service.getWalletByUserId(userId)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{userId}/addItemToWalletByUserID", response_model=Wallet)
def addItemToWallet(userId: int, symbol: str, amount: float,service:WalletService = Depends(wallet_service)):
    try:
        return service.addItemToWallet(userId, symbol, amount)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/exists/{userId}")
def walletExists(userId: int, service: WalletService = Depends(wallet_service)) -> bool:
    try:
        return service.walletExists(userId)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/{userId}")
def deleteWallet(userId: int, service: WalletService = Depends(wallet_service)):
    try:
        service.deleteWallet(userId)
        return {"message": f"Wallet for user {userId} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{userId}/item/{symbol}", response_model=Wallet)
def removeItemFromWallet(userId: int, symbol: str, service: WalletService = Depends(wallet_service)):
    try:
        return service.removeItemFromWallet(userId, symbol)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{userId}/item/{symbol}", response_model=Wallet)
def updateItemAmount(userId: int, symbol: str, amount: float, service: WalletService = Depends(wallet_service)):
    try:
        return service.updateItemAmount(userId, symbol, amount)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

