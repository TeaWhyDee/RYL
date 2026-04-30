from typing import Iterator
import pytest
from unittest.mock import patch
import sqlalchemy as sqla
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.utility.context import ContextValues

# Example: export TEST_DATABASE_URL="postgresql://user:pass@localhost:5432/test_db"
# TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
# TODO load env
TEST_DATABASE_URL = "postgresql://ryl_dev:ryl_dev1@localhost:5432/ryl_test"


@pytest.fixture(scope="session")
def engine():
    if not TEST_DATABASE_URL:
        raise RuntimeError("TEST_DATABASE_URL env variable must be set")

    engine = create_engine(TEST_DATABASE_URL)

    # Recreate schema fresh for the test session
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    return engine


@pytest.fixture(scope="function")
def session(engine):
    """
    Creates a DB connection and wraps each test in a SAVEPOINT so the database
    is rolled back to a clean state after every test.
    """
    connection = engine.connect()
    transaction = connection.begin()  # outer transaction

    SessionLocal = sessionmaker(
        bind=connection, autoflush=False, autocommit=False
    )
    session = SessionLocal()

    # Start a nested transaction (SAVEPOINT)
    nested = connection.begin_nested()

    # Restart SAVEPOINT when needed (e.g., if test triggers IntegrityError)
    @sqla.event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            nonlocal nested
            nested = connection.begin_nested()

    yield session

    session.close()
    transaction.rollback()  # rolls back the whole test
    connection.close()


@pytest.fixture
def ctx_mock():
    class MockContextValues(object):
        user_id = "0"
        note = "test"

        def set(self):
            return

    return MockContextValues()


@pytest.fixture(scope="session")
def db_patch() -> Iterator[None]:
    with patch("app.db.services.user.db.session.add"), patch(
        "app.db.services.user.db.session.commit"
    ):
        yield
