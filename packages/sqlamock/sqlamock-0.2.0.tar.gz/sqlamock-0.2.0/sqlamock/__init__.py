"""sqlamock: A SQL Database Mocking Library
==========================================

Usage Examples
--------------

1. Mocking tables using a dictionary:

    def test_default_interface(db_mock):
        with db_mock.from_dict({"table": [{"column": "other_column"}]}) as mocked_data:
            fetched_column = fetch_table_by_column("other_column")
            assert fetched_column.id == mocked_data["table"][0]["id"]

2. Mocking tables using ORM models:

    def test_using_orm_classes(db_mock):
        with db_mock.from_orm([MyModel(column="foo")]) as mocked_data:
            fetched_column = fetch_table_by_column("other_column")
            assert fetched_column.id == mocked_data[MyModel][0]["id"]

3. Loading mock data from a file:

    def test_loading_from_file(db_mock):
        with db_mock.from_file("mock_data/bulk_operations.json") as mocked_data:
            pass

Configuration
-------------

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from db import *  # noqa # load schemas
from models.base import BaseModel
from sqlamock.fixtures import *  # noqa

if TYPE_CHECKING:
    from sqlamock import MockConnectionProvider, Patches


@pytest.fixture(scope="session")
def db_mock_base_model():
    return BaseModel


@pytest.fixture(scope="session")
def db_mock_session(db_mock_patches: "Patches", db_mock_connection: "MockConnectionProvider"):
    db_mock_patches.add_patch(patch("app.models.connect.SessionLocal", db_mock_connection.get_session))



Example Test
------------

def test_model_create(db_mock: "DBMock", db_mock_connection: "MockConnectionProvider"):
    session = db_mock_connection.get_session()
    with db_mock.from_orm(
        [Model()]
    ) as mocked_data:
        repo = session.query(Model).first()
        assert repo.id == mocked_data[Model][0].id

"""

# Easier imports for typing or whatever :)
from .connection_provider import MockConnectionProvider
from .data_interface import MockDataInterface
from .db_mock import DBMock
from .patches import Patches

__all__ = [
    "DBMock",
    "MockConnectionProvider",
    "MockDataInterface",
    "Patches",
]
