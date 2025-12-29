import email
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.domain.models.user import User
from app.domain.services.userService import UserService


def test_login_with_google_if_not_exists():
    userRepo = Mock()
    userRepo.get_by_email.return_value = None

    createdUser = User(
        id=1,
        email='allan@gmail.com',
        username='Allan',
        createdAt=datetime.now(timezone.utc),
    )

    userRepo.create.return_value = createdUser
    service = UserService(userRepo=userRepo)

    googleData = {
        'email': 'allan@gmail.com',
        'name': 'Allan',
    }

    result = service.login_with_google(googleData)

    assert result == createdUser
    userRepo.get_by_email.assert_called_once_with("allan@gmail.com")
    userRepo.create.assert_called_once()

    new_user_arg = userRepo.create.call_args[0][0]

    assert new_user_arg.id is None
    assert new_user_arg.email == "allan@gmail.com"
    assert new_user_arg.username == "Allan"
    assert isinstance(new_user_arg.createdAt, datetime)


def test_login_with_google_raises_if_email_missing():
    userRepo = Mock()
    service = UserService(userRepo)

    googleData = {"name":"Allan"}

    with pytest.raises(ValueError):
        service.login_with_google(googleData)

    userRepo.get_by_email.assert_not_called()
    userRepo.create.assert_not_called()

def test_login_with_google_returns_existing_user():
    userRepo = Mock()
    existing_user = User(
        id=1,
        email="allan@gmail.com",
        username="allan",
        createdAt=datetime.now(timezone.utc)
    )
    userRepo.get_by_email.return_value = existing_user
    service = UserService(userRepo)

    googleData = {"name":"Allan", "email":"allan@gmail.com"}

    result = service.login_with_google(googleData)

    assert result == existing_user
    userRepo.get_by_email.assert_called_with(existing_user.email)
    userRepo.create.assert_not_called()
