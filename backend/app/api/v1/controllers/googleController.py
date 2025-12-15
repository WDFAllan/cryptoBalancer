from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os

from app.core.config import oauth
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_SECONDS
from app.core.database.database import get_db
from app.infrastructure.repository.userRepository import UserRepository
from app.domain.services.userService import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])

def google_service(db:Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))

@router.get("/google/login")
async def google_login(request: Request):
    try:
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/auth/google/callback")
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initiate Google login")

@router.get("/google/callback")
async def google_callback(
        request: Request,
        userService:UserService = Depends(google_service)
):
    try:
        token = await oauth.google.authorize_access_token(request)
        
        nonce = request.session.get("nonce") or request.session.get("oidc_nonce")
        google_data = await oauth.google.parse_id_token(token, nonce)

        user = userService.login_with_google(google_data)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create or retrieve user")
        
        jwt_token = create_access_token(user.email)
        
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")

        response = RedirectResponse(url=f"{frontend_url}/", status_code=302)
        
        is_production = os.getenv("ENVIRONMENT", "development") == "production"
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_SECONDS
        )
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
        return RedirectResponse(url=f"{frontend_url}/login?error=auth_failed", status_code=302)