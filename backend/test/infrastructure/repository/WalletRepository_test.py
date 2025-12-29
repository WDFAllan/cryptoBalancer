import types
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.database.database import Base
from app.infrastructure.repository.walletRepository import WalletRepository
from app.infrastructure.models.wallet.walletTable import WalletTable
from app.infrastructure.models.wallet.walletItemTable import WalletItemTable
from app.domain.models.wallet.walletItem import WalletItem


@pytest.fixture
def db_session():
    # engine en mémoire
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # créer toutes les tables en mémoire
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
        db.rollback()
    finally:
        db.close()


def test_create_wallet_persist(db_session):
    
    repo = WalletRepository(db_session)

    wallet = repo.createWallet(userId=1)

    assert wallet.userId == 1
    assert wallet.items == []

    saved = db_session.query(WalletTable).filter_by(userId=1).first()
    assert saved is not None


def test_add_to_wallet_adds_new_item(db_session):
    repo = WalletRepository(db_session)

    repo.createWallet(userId=2)

    item = WalletItem(id=None, symbol="BTC", amount=2.5)
    wallet = repo.addToWallet(userId=2, walletItem=item)

    assert wallet.userId == 2
    assert any(i.symbol == "BTC" and i.amount == 2.5 for i in wallet.items)

    saved_item = db_session.query(WalletItemTable).filter_by(symbol="BTC").first()
    assert saved_item is not None
    assert saved_item.amount == 2.5


def test_add_to_wallet_increments_existing_item(db_session):
    
    repo = WalletRepository(db_session)

    repo.createWallet(userId=3)

    repo.addToWallet(userId=3, walletItem=WalletItem(id=None, symbol="ETH", amount=1.0))
    wallet = repo.addToWallet(userId=3, walletItem=WalletItem(id=None, symbol="ETH", amount=2.0))

    eth_items = [i for i in wallet.items if i.symbol == "ETH"]
    assert len(eth_items) == 1
    assert pytest.approx(eth_items[0].amount) == 3.0


def test_get_wallet_by_userid_returns_none_when_missing(db_session):
    repo = WalletRepository(db_session)

    assert repo.getWalletByUserId(userId=999) is None


def test_get_wallet_by_userid_returns_wallet(db_session):
    repo = WalletRepository(db_session)

    repo.createWallet(userId=4)
    repo.addToWallet(userId=4, walletItem=WalletItem(id=None, symbol="XRP", amount=10.0))

    wallet = repo.getWalletByUserId(userId=4)
    assert wallet is not None
    assert wallet.userId == 4
    assert any(i.symbol == "XRP" for i in wallet.items)
