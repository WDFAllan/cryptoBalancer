from fastapi import APIRouter
from app.domain.services.cryptoService import CryptoService
from app.infrastructure.repository.cryptoRepository import CryptoRepository

router = APIRouter()
service = CryptoService(CryptoRepository())

@router.get("/price/{symbol}")
async def get_price(symbol: str):
    price = await service.get_crypto_price(symbol)
    return {"symbol": symbol, "price": price}
