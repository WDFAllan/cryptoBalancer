from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.services.backtestService import BacktestService
from app.domain.strategies.BaseParams import BaseParams
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository

router = APIRouter(prefix="/strategy", tags=["Strategy"])

def get_daily_candle_repo(db: Session = Depends(get_db)):
    return dailyCandleRepository(db)

def backtestService(dailyCandleRepo: dailyCandleRepository = Depends(get_daily_candle_repo)):
    return BacktestService(dailyCandleRepo=dailyCandleRepo)


@router.post("/{strategy_name}", response_model=None)
def run_any_strategy(strategy_name: str, service = Depends(backtestService)):
    result_df = service.runStrategy(strategy_name)
    return result_df.to_dict(orient="records")

