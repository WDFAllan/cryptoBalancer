from app.domain.models.user import User
from app.infrastructure.models.userTable import UserTable
from app.core.database.database import SessionLocal


class UserRepository:

    def __init__(self):
        self.db = SessionLocal()

    def get_by_email(self, email: str):
        entity = self.db.query(UserTable).filter(UserTable.email == email).first()
        if not entity:
            return None
        return User(id=entity.id, email=entity.email, username=entity.username)

    def create(self, user: User):
        entity = UserTable(
            email=user.email,
            username=user.username
        )
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return User(id=entity.id, email=entity.email, username=entity.username)
