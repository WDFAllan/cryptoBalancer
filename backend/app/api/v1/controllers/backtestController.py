from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.services.backtestService import BacktestService
from app.domain.services.walletService import WalletService
from app.domain.strategies.BaseParams import BaseParams
from app.infrastructure.repository.candle.dailyCandleRepository import dailyCandleRepository
from app.infrastructure.repository.walletRepository import WalletRepository
from app.infrastructure.repository.userRepository import UserRepository

router = APIRouter(prefix="/strategy", tags=["Strategy"])

def get_daily_candle_repo(db: Session = Depends(get_db)):
    return dailyCandleRepository(db)

def backtestService(db: Session = Depends(get_db)):
    dailyCandleRepo = dailyCandleRepository(db)
    walletRepo = WalletRepository(db)
    userRepo = UserRepository(db)
    walletService = WalletService(walletRepo)
    return BacktestService(dailyCandleRepo=dailyCandleRepo, walletService=walletService, userRepo=userRepo)


@router.post("/{strategy_name}", response_model=None)
def run_any_strategy(
        strategy_name: str,
        userId:int,
        service = Depends(backtestService)):
    result_df = service.runStrategy(strategy_name, userId)
    if(strategy_name != "constant_mix"):
       response = {
            "data": result_df.to_dict(orient="records")
        } 
    else:
        response = {
            "meilleur": result_df.attrs.get('best_mode'),
            "data": result_df.to_dict(orient="records")
        }
    return response

