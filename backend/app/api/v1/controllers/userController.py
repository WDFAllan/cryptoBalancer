from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database.database import get_db
from app.core.security import get_current_user
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


@router.put("/updateFavoritePlatform", response_model=User)
def update_favorite_platform(user_id: int, favorite_platform: str, service: UserService = Depends(user_service)):
    try:
        updated_user = service.update_favorite_platform(user_id, favorite_platform)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/getUser/me", response_model=User)
def get_current_user_route(service: UserService = Depends(user_service), current_user: User = Depends(get_current_user)):
    try:
        return service.getUserByEmail(current_user.email)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 

