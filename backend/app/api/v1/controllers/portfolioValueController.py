from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.models.portfolioValue import PortfolioValue
from app.domain.services.portfolioValueService import PortfolioValueService
from app.domain.services.cryptoService import CryptoService
from app.infrastructure.repository.portfolioValueRepository import PortfolioValueRepository
from app.infrastructure.repository.walletRepository import WalletRepository
from app.infrastructure.repository.cryptoRepository import CryptoRepository
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.adapters.binanceCandleAdapter import binanceCandleAdapter
from app.domain.services.candle.dailyCandleService import dailyCandleService

router = APIRouter(prefix="/portfolio-value", tags=["Portfolio Value"])


def portfolio_value_service(db: Session = Depends(get_db)) -> PortfolioValueService:
    portfolioValueRepo = PortfolioValueRepository(db)
    walletRepo = WalletRepository(db)
    cryptoService = CryptoService(CryptoRepository())
    candleService = dailyCandleService(dailyCandleRepository(db), CryptoRepository(), binanceCandleAdapter())
    return PortfolioValueService(portfolioValueRepo, walletRepo, cryptoService, candleService)



@router.post("/{userId}/calculate", response_model=PortfolioValue)
async def calculateAndSavePortfolioValue(
    userId: int,
    service: PortfolioValueService = Depends(portfolio_value_service)
):
    """
    Calcule la valeur actuelle du portefeuille et la sauvegarde.
    """
    try:
        return await service.calculateAndSavePortfolioValue(userId)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{userId}/history", response_model=List[PortfolioValue])
def getPortfolioValueHistory(
    userId: int,
    service: PortfolioValueService = Depends(portfolio_value_service)
):
    """
    Récupère tout l'historique des valeurs du portefeuille pour un utilisateur.
    """
    try:
        return service.getPortfolioValueHistory(userId)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{userId}/history/range", response_model=List[PortfolioValue])
def getPortfolioValueByDateRange(
    userId: int,
    startDate: datetime = Query(..., description="Date de début (format ISO: YYYY-MM-DD)"),
    endDate: datetime = Query(..., description="Date de fin (format ISO: YYYY-MM-DD)"),
    service: PortfolioValueService = Depends(portfolio_value_service)
):
    """
    Récupère l'historique des valeurs du portefeuille pour une période donnée.
    """
    try:
        return service.getPortfolioValueByDateRange(userId, startDate, endDate)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{userId}/latest", response_model=PortfolioValue)
def getLatestPortfolioValue(
    userId: int,
    service: PortfolioValueService = Depends(portfolio_value_service)
):
    """
    Récupère la dernière valeur sauvegardée du portefeuille.
    """
    try:
        value = service.getLatestPortfolioValue(userId)
        if not value:
            raise HTTPException(status_code=404, detail=f"No portfolio value found for user {userId}")
        return value
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{userId}/daily", response_model=List[PortfolioValue])
async def getListDailyPortfolioValue(
    userId: int,
    service: PortfolioValueService = Depends(portfolio_value_service)
):
    """
    Récupère les valeurs quotidiennes du portefeuille pour un utilisateur.
    """
    try:
        return await service.calculateDailyPortfolioValue(userId)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))