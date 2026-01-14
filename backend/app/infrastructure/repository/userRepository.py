from datetime import datetime, timezone

from sqlalchemy.orm import Session
from app.domain.models.user import User
from app.domain.port.userPort import IUserPort
from app.infrastructure.models.userTable import UserTable


class UserRepository(IUserPort):

    def __init__(self,db: Session):
        self.db = db

    def update_favorite_platform(self, user_id: int, favorite_platform: str) -> User:
        entity = self.db.query(UserTable).filter_by(id=user_id).first()
        if not entity:
            return None
        entity.favorite_platform = favorite_platform
        self.db.commit()
        self.db.refresh(entity)
        return User(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            createdAt=entity.createdAt,
            favorite_platform=getattr(entity, "favorite_platform", None)
        )

    def get_by_id(self, user_id: int):
        entity = self.db.query(UserTable).filter_by(id=user_id).first()
        if not entity:
            return None
        return User(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            createdAt=entity.createdAt,
            favorite_platform=getattr(entity, "favorite_platform", None)
        )

    def get_by_email(self, email: str):
        entity = self.db.query(UserTable).filter_by(email = email).first()
        if not entity:
            return None

        return User(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            createdAt=entity.createdAt,
            favorite_platform=getattr(entity, "favorite_platform", None)
        )

    def create(self, user: User):
        entity = UserTable(
            email=user.email,
            username=user.username,
            favorite_platform=user.favorite_platform
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return User(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            createdAt=entity.createdAt,
            favorite_platform=getattr(entity, "favorite_platform", None)
        )
