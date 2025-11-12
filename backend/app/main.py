from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.v1.controllers.cryptoController import router as crypto_router
from app.api.v1.controllers.googleController import router as google_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.database.db_init import init_db
from dotenv import load_dotenv
import os

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
app.include_router(crypto_router, prefix="/api/v1")
app.include_router(google_router, prefix="/api/v1")

