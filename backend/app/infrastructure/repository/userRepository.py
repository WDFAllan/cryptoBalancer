from sqlalchemy.orm import Session
from app.domain.models.user import User
from app.domain.port.userPort import IUserPort
from app.infrastructure.models.userTable import UserTable


class UserRepository(IUserPort):

    def __init__(self,db: Session):
        self.db = db

    def get_by_email(self, email: str):
        entity = self.db.query(UserTable).filter_by(email = email).first()
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
