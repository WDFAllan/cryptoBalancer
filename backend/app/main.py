from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.controllers.cryptoController import router as crypto_router
from app.api.v1.controllers.googleController import router as google_router
from app.api.v1.controllers.walletController import router as wallet_router
from app.api.v1.controllers.candleController import router as candle_router
from app.api.v1.controllers.userController import router as user_router
from starlette.middleware.sessions import SessionMiddleware


from app.core.database.db_init import init_db
from dotenv import load_dotenv
import os

from app.core.scheduler.candleScheduler import registerCandleScheduler

load_dotenv()

app = FastAPI(title="Crypto Balancer API")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.include_router(crypto_router, prefix="/api/v1")
app.include_router(user_router,prefix="/api/v1")
app.include_router(google_router, prefix="/api/v1")
app.include_router(wallet_router, prefix="/api/v1")
app.include_router(candle_router, prefix="/api/v1")

@app.on_event("startup")
def startup_event():
    print("🔌 Initialisation de la base de données…")
    init_db()
    print("✅ Base de données prête")

registerCandleScheduler(app)