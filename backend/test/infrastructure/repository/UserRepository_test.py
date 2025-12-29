import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database.database import Base
from app.infrastructure.repository.userRepository import UserRepository
from app.infrastructure.models.userTable import UserTable
from app.domain.models.user import User


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


def test_get_by_email_returns_none_when_not_found(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_email("noone@example.com") is None


def test_create_persists_and_returns_user(db_session):
    repo = UserRepository(db_session)

    user_domain = User(id=None, email="alice@example.com", username="alice", createdAt=None)
    created = repo.create(user_domain)

    assert created.id is not None
    assert created.email == "alice@example.com"
    assert created.username == "alice"

    saved = db_session.query(UserTable).filter_by(email="alice@example.com").first()
    assert saved is not None
    assert saved.username == "alice"


def test_get_by_email_returns_user(db_session):
    repo = UserRepository(db_session)

    user_domain = User(id=None, email="bob@example.com", username="bob", createdAt=None)
    repo.create(user_domain)

    found = repo.get_by_email("bob@example.com")
    assert found is not None
    assert found.email == "bob@example.com"
    assert found.username == "bob"
