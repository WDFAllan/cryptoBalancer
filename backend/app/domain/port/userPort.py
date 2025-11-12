from abc import ABC, abstractmethod
from app.domain.models.user import User

class IUserPort(ABC):


    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def create(self, entity: User) -> User:
        pass