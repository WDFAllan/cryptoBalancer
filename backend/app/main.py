from fastapi import FastAPI
from app.api.v1.endpoints.crypto_endpoints import router as crypto_router

app = FastAPI()

app.include_router(crypto_router, prefix="/api/v1")
