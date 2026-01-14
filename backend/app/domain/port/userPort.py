from abc import ABC, abstractmethod
from app.domain.models.user import User

class IUserPort(ABC):


    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        pass
    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    def create(self, entity: User) -> User:
        pass

    @abstractmethod
    def update_favorite_platform(self, user_id: int, favorite_platform: str) -> User:
        pass