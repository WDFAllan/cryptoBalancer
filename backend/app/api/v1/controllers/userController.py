from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.domain.models.user import User
from app.domain.services.userService import UserService
from app.infrastructure.repository.userRepository import UserRepository

router = APIRouter(prefix="/user", tags=["User"])

def user_service(db:Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.get("/getUserByEmail/{email}", response_model=User)
def getUserByEmail(email: str, service: UserService = Depends(user_service)):
    try:
        return service.getUserByEmail(email)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



