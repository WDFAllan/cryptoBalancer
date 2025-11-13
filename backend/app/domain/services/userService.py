from app.domain.models.user import User
from app.domain.port.userPort import IUserPort
from app.infrastructure.repository.userRepository import UserRepository


class UserService:

    def __init__(self, userRepo:IUserPort):
        self.userRepo = userRepo

    def login_with_google(self, google_data: dict):
        email = google_data.get("email")
        username = google_data.get("name")

        user = self.userRepo.get_by_email(email)
        if user:
            return user

        new_user = User(id=None, email=email, username=username)
        return self.userRepo.create(new_user)
