from collections import defaultdict
from typing import TYPE_CHECKING, Generic

from .types import BaseType

if TYPE_CHECKING:
    from collections.abc import Iterable


class MockDataInterface(Generic[BaseType]):
    """A class that provides an interface for accessing mocked database data.

    This class organizes and provides access to mocked database instances,
    allowing retrieval by both ORM class and table name for QOL purposes.

    This is returned by the db_mock entered context. It is primarily useful for retrieving
    dynamically determined column values like primary keys for further assertions.

    Attributes:
        data_registry (dict): A dictionary mapping ORM classes to lists of their instances.
        table_name_mapping (dict): A dictionary mapping table names to their corresponding ORM classes.
    """

    if TYPE_CHECKING:
        data_registry: dict[type[BaseType], list[BaseType]]
        table_name_mapping: dict[str, type[BaseType]]

    def __init__(self, instances: "Iterable[BaseType]"):
        """Initialize the MockDataInterface with a list of ORM instances.

        This method populates the data_registry and table_name_mapping
        based on the provided instances.

        Args:
            instances (list[BaseType]): A list of SQLAlchemy ORM instances.
        """
        self.data_registry = defaultdict(list)
        self.table_name_mapping = {}

        for instance in instances:
            self.data_registry[type(instance)].append(instance)

        for key in self.data_registry.keys():
            self.table_name_mapping[key.__tablename__] = key

    def __getitem__(self, key: "type[BaseType] | str") -> list["BaseType"]:
        """Retrieve mocked data instances by ORM class or table name.

        This method allows accessing mocked data using either the ORM class
        or the table name as a key.

        Args:
            key (type[BaseType] | str): The ORM class or table name to retrieve data for.

        Returns:
            list[BaseType]: A list of mocked data instances for the specified key.

        Raises:
            KeyError: If the provided key is not found in the data registry or table name mapping.
        """
        if isinstance(key, str):
            try:
                return self.data_registry[self.table_name_mapping[key]]
            except KeyError as e:
                raise KeyError(f"Table name {key} not found") from e

        return self.data_registry[key]
