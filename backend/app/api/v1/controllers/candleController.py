from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.services.candle.dailyCandleService import dailyCandleService
from app.domain.services.candle.threeMinCandleService import threeMinutesCandleService
from app.infrastructure.adapters.binanceCandleAdapter import binanceCandleAdapter

from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.repository.candle.threeMinCandleRepository import threeMinCandleRepository

from app.infrastructure.repository.cryptoRepository import CryptoRepository

router = APIRouter(prefix="/candle", tags=["Candle"])

def candle1d_service(db:Session = Depends(get_db)) -> dailyCandleService:
    return dailyCandleService(
        dailyCandleRepository(db),
        CryptoRepository(),
        binanceCandleAdapter()
    )

def candle3m_service(db:Session = Depends(get_db)) -> threeMinutesCandleService:
    return threeMinutesCandleService(
        threeMinCandleRepository(db),
        CryptoRepository(),
        binanceCandleAdapter()
    )

@router.get("/getTwoYearsCandles")
async def getTwoYearsCandles(service: dailyCandleService = Depends(candle1d_service)):
    try:
        return await service.syncPeriod(730)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getCandlesBySymbol/{symbol}")
def getCandlesBySymbol(symbol: str, service: dailyCandleService = Depends(candle1d_service)):
    try:
        return service.getCandlesBySymbol(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getThreeMinutesCandles")
async def getThreeMinutesCandles(service: threeMinutesCandleService = Depends(candle3m_service)):
    try:
        return await service.syncPeriod(2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getCandles3MBySymbol/{symbol}")
def getCandlesBySymbol(symbol: str, service: threeMinutesCandleService = Depends(candle3m_service)):
    try:
        return service.getCandlesBySymbol(symbol)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
