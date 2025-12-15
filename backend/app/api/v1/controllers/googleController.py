from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
import os

from app.core.config import oauth
from app.core.security import create_access_token
from app.core.database.database import get_db
from app.infrastructure.repository.userRepository import UserRepository
from app.domain.services.userService import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])

def google_service(db:Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(
        request: Request,
        userService:UserService = Depends(google_service)
):

    token = await oauth.google.authorize_access_token(request)
    nonce = request.session.get("nonce") or request.session.get("oidc_nonce")
    google_data = await oauth.google.parse_id_token(token, nonce)

    user = userService.login_with_google(google_data)
    token = create_access_token(user.email)
    return {"access_token": token, "token_type": "bearer"}
    
