import json
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING, Generic

from sqlalchemy import Index, Integer, inspect
from sqlalchemy.schema import CreateIndex

from sqlamock.patches import Patches

from .data_interface import MockDataInterface
from .snapshot import Snapshot
from .types import BaseType

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from contextlib import AbstractContextManager
    from pathlib import Path

    from sqlalchemy import MetaData

    from .connection_provider import ConnectionProvider
    from .data_interface import MockDataInterface


class DBMock(Generic[BaseType]):
    """A class that provides a mock interface for simulating interactions with
    multiple database tables in unit tests.

    This class validates the mocked data against the current state of the SQLAlchemy
    schemas, ensuring that the mock data aligns with the actual table and column
    definitions in the database models. The context managers returned by this class
    can be scoped to the fixture they are provided in, ensuring that each test
    maintains isolated and clean data. Different database data mocks can be applied
    at different scopes and layers. For example, you can provide default data for
    all tests, but within a test, apply additional data for a specific test function,
    or for managing multiple data contexts within the same test.

    Features:
    ---------
    - **Mock Data Across Tables**: Provides an interface to mock data for multiple
      tables, validated against the current SQLAlchemy schemas.
    - **Fixture Scoped Data**: The mocked data is scoped according to the fixture
      (e.g., function, module) it is provided in, ensuring that each test maintains
      isolated and clean data.
    - **No External Resources**: Supports unit testing without needing separately
      provisioned resources, such as a real database, allowing tests to run faster
      and in isolation.
    - **Foreign Key Support**: Allows defining foreign keys and creating rows across
      related tables, ensuring that relationships between tables are respected in
      the mock data.
    - **Isolated Mock Instances**: Each mock instance maintains its own state,
      allowing multiple test cases or fixtures to apply separate layers of data
      without conflict.
        - Example: You can have a default mock database state and apply additional
          test-specific data layers that are cleaned up when out of scope.
        - Limitation: Constraints across different mock instances will break. All
          data related to a test must be created within a single mock instance to
          remain isolated and valid.

    Methods:
    --------
    from_dict(data: dict[str, list[dict]]):
        Mocks multiple tables and their rows using a dictionary format, ensuring
        data consistency with SQLAlchemy schemas.

    from_orm(models: list[Base]):
        Mocks multiple database tables using SQLAlchemy ORM model instances,
        supporting relationships between tables and foreign keys.

    from_file(file_path: Path | str):
        Loads mock data for multiple tables from a JSON file, simulating tables
        with relationships, and bulk operations.
    """

    if TYPE_CHECKING:
        base: type[BaseType]
        connection_provider: ConnectionProvider
        database_initialized: bool
        patches: Patches

    def __init__(
        self,
        base: "type[BaseType]",
        connection_provider: "ConnectionProvider",
        patches: "Patches",
    ):
        self.base = base
        self.connection_provider = connection_provider
        self.database_initialized = False
        self.patches = patches

    @property
    def metadata(self) -> "MetaData":
        return self.base.metadata

    @cached_property
    def orm_classes(self) -> dict[str, "type[BaseType]"]:
        return {
            mapper.entity.__tablename__: mapper.entity
            for mapper in self.base.registry.mappers
        }

    def from_dict(
        self, data: dict[str, list[dict]]
    ) -> "AbstractContextManager[MockDataInterface]":
        """Mock multiple tables and their rows using a dictionary.

        Args:
        -----
        data (dict): Dictionary where the key is the table name and the value is
                     a list of rows (each row being a dictionary of column data).

        Returns:
        -------
        ContextManager[MockedDataInterface]: Mocked data interface containing
                                             created data by table and rows.
        """
        instances = [
            self.orm_classes[table_name](**row)
            for table_name, rows in data.items()
            for row in rows
        ]
        return self.from_orm(instances)

    def from_file(
        self, file_path: "Path | str"
    ) -> "AbstractContextManager[MockDataInterface]":
        """Load mock data for multiple tables from a JSON file and simulate
        relationships between tables.

        Args:
        -----
        file_path (str): Path to the JSON file containing mock data for multiple tables.

        Returns:
        -------
        ContextManager[MockedDataInterface]: Mocked data interface containing
                                             created data by table and rows.
        """
        with open(file_path) as f:
            data = json.load(f)
        return self.from_dict(data)

    @contextmanager
    def from_orm(
        self, instances: "Iterable[BaseType]"
    ) -> "Generator[MockDataInterface, None, None]":
        """Mock multiple database tables using SQLAlchemy ORM model instances.

        Args:
        -----
        instances (list): List of SQLAlchemy ORM model instances representing
                          rows in the database tables.

        Returns:
        -------
        Generator[MockedDataInterface, None, None]: A generator yielding a mocked
                                                    data interface containing
                                                    created data by table and rows.
        """
        with self.patches:
            self.init_database()
            with Snapshot(self.connection_provider):
                with self.connection_provider.get_session() as session:
                    session.add_all(instances)
                    session.commit()
                    for instance in instances:
                        session.refresh(instance)

                db_mock_context: MockDataInterface = MockDataInterface(
                    instances=instances
                )
                yield db_mock_context

    def init_database(self):
        if self.database_initialized:
            return

        tables_to_create = set()

        engine = self.connection_provider.get_engine()
        inspection = inspect(engine)

        for table in self.base.metadata.sorted_tables:
            if not inspection.has_table(table.name, schema=table.schema):
                tables_to_create.add(table)

            for column in table.columns:
                # note: addreses a limitation of SQLite in which Identity is not recognized as
                # a column to auto generate values for. We must pass in autoincrement explicitly to achieve
                # the same effect.
                if column.primary_key and column.type.python_type is int:
                    column.autoincrement = True
                    column.type = Integer()

        for table_to_create in tables_to_create:
            indexes_with_postgresql_where = []
            indexes_to_remove = []

            for index in list(table_to_create.indexes):
                if index.name and hasattr(index, "dialect_options"):
                    postgresql_opts = index.dialect_options.get("postgresql", {})
                    postgresql_where = postgresql_opts.get("where")
                    if postgresql_where is not None:
                        indexes_with_postgresql_where.append((index, postgresql_where))
                        indexes_to_remove.append(index)

            for index in indexes_to_remove:
                table_to_create.indexes.discard(index)

            table_to_create.create(engine)

            for index, postgresql_where in indexes_with_postgresql_where:
                existing_indexes = inspection.get_indexes(
                    table_to_create.name, schema=table_to_create.schema
                )
                existing_index_names = {idx["name"] for idx in existing_indexes}

                if index.name not in existing_index_names:
                    index_to_create = Index(
                        index.name,
                        *[col for col in index.columns],
                        unique=index.unique,
                        sqlite_where=postgresql_where,
                    )
                    try:
                        with engine.connect() as conn:
                            conn.execute(CreateIndex(index_to_create))
                            conn.commit()
                    except Exception as e:
                        # Index might already exist or there might be another issue
                        # Silently continue as the index may have been created by table.create()
                        pass

        self.database_initialized = True
