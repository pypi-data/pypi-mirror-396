from typing import TYPE_CHECKING

import pytest

from sqlamock.patches import Patches

from .async_connection_provider import MockAsyncConnectionProvider
from .async_db_mock import AsyncDBMock

if TYPE_CHECKING:
    from .types import BaseType


@pytest.fixture(scope="session")
def db_mock_async_connection() -> "MockAsyncConnectionProvider":
    return MockAsyncConnectionProvider()


@pytest.fixture(scope="session")
def db_mock_async(
    db_mock_async_connection: "MockAsyncConnectionProvider",
    db_mock_base_model: "type[BaseType]",
    db_mock_patches: "Patches",
) -> "AsyncDBMock":
    return AsyncDBMock(db_mock_base_model, db_mock_async_connection, db_mock_patches)
