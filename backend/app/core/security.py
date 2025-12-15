import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.infrastructure.repository.userRepository import UserRepository


SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGO", "HS256")
ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("JWT_EXPIRES", "3600"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/google/login", auto_error=False)


def create_access_token(subject: str) -> str:
    """Generate a short-lived JWT for the given subject (email/id)."""
    if not SECRET_KEY:
        raise RuntimeError("JWT_SECRET is not set")

    expire = datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=401, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        payload = decode_token(token)
        email: Optional[str] = payload.get("sub")
    except JWTError as e:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not email:
        raise HTTPException(
            status_code=401, 
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = UserRepository(db).get_by_email(email)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user