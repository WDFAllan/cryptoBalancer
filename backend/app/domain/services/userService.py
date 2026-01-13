from datetime import timezone, datetime

from app.domain.models.user import User
from app.domain.port.userPort import IUserPort
from app.infrastructure.repository.userRepository import UserRepository


class UserService:

    def __init__(self, userRepo:IUserPort):
        self.userRepo = userRepo

    def update_favorite_platform(self, user_id: int, favorite_platform: str) -> User:
        return self.userRepo.update_favorite_platform(user_id, favorite_platform)

    def login_with_google(self, google_data: dict):
        email = google_data.get("email")
        username = google_data.get("name")
        
        if not email:
            raise ValueError("Email is required from Google authentication")
        
        createdAt = datetime.now(timezone.utc)

        user = self.userRepo.get_by_email(email)
        if user:
            return user

        new_user = User(id=None, email=email, username=username, createdAt=createdAt, favorite_platform=None)
        created_user = self.userRepo.create(new_user)
        return created_user

    def getUserById(self, user_id: int):
        user = self.userRepo.get_by_id(user_id)
        if user:
            return user
        return None

    def getUserByEmail(self, email):
        user = self.userRepo.get_by_email(email)
        if user:
            return user
        return None
