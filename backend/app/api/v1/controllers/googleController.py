from fastapi import APIRouter, Request
from app.core.config import oauth
from app.infrastructure.repository.userRepository import UserRepository
from app.domain.services.userService import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    print(token)
    nonce = request.session.get("nonce") or request.session.get("oidc_nonce")

    google_data = await oauth.google.parse_id_token(token,nonce)

    user_service = UserService(UserRepository())
    user = user_service.login_with_google(google_data)

    return {
        "message": "Logged in",
        "user": user
    }
