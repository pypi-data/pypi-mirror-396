from typing import TYPE_CHECKING

import pytest
from sqlalchemy.orm import declarative_base

from sqlamock.patches import Patches

from .connection_provider import MockConnectionProvider
from .db_mock import DBMock

if TYPE_CHECKING:
    from .connection_provider import ConnectionProvider
    from .types import BaseType


@pytest.fixture(scope="session")
def db_mock_base_model() -> "type[BaseType]":
    """Fixture that is used as an interface to provide the base SQLAlchemy declarative model used
    in schemas to be tested.

    This also requires that your schemas are imported and registered to the base model at some point
    before db_mock context.

    Returns:
        type[SQLAlchemyORMProtocol]: SQLAlchemy declarative model
    """
    return declarative_base()


@pytest.fixture(scope="session")
def db_mock_connection() -> "ConnectionProvider":
    """Fixture that provides a mock database connection for testing.

    This fixture sets up a mock database connection using MockConnectionProvider.
    It is expected that this fixture is used in another fixture that patches the session or engine provider
    in the code to be tested.

    Note: the engine is recycled, so if the code caches an engine, this interface cannot be used to patch that engine
    Instead the session provider should be patched. Surely, the session is not cached...

    Yields:
        MockConnectionProvider: An instance of MockConnectionProvider for use in patching.
    """
    return MockConnectionProvider()


@pytest.fixture(scope="session")
def db_mock_patches() -> "Patches":
    return Patches()


@pytest.fixture(scope="session")
def db_mock(
    db_mock_connection: "ConnectionProvider",
    db_mock_base_model: "type[BaseType]",
    db_mock_patches: "Patches",
) -> "DBMock":
    """Fixture that provides the main DBMock interface for database data mocking in tests.

    This fixture creates and returns a DBMock instance, which can be used to
    mock database operations in tests. Please see db_mock.py::DBMock for more information.

    Args:
        db_mock_connection (MockConnectionProvider): The mock connection provider.
        db_mock_base_model (type[SQLAlchemyORMProtocol]): The base SQLAlchemy model.

    Returns:
        DBMock: An instance of DBMock for use in tests.
    """
    return DBMock(db_mock_base_model, db_mock_connection, db_mock_patches)
