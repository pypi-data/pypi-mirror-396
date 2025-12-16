import tempfile
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session


class MockConnectionProvider:
    """A class that provides mock database connections for patching purposes.

    This class creates and manages SQLite in-memory(file) databases, which can be used
    as a lightweight replacement for actual database connections in tests.

    Attributes:
        engine_kwargs (dict): Additional keyword arguments to pass to create_engine.
    """

    if TYPE_CHECKING:
        engine_kwargs: dict

    def __init__(self, engine_kwargs: dict | None = None):
        """Initialize a new MockConnectionProvider instance.

        Args:
            engine_kwargs (dict | None): Additional keyword arguments to pass to create_engine.
                                         If None, an empty dict will be used.
        """
        self.engine_kwargs = engine_kwargs or {}

    @lru_cache  # noqa: B019
    def get_engine(self) -> Engine:
        """Get or create a SQLAlchemy engine instance.

        This method creates a new SQLite in-memory database engine. The result is
        cached, so subsequent calls will return the same engine instance.

        Returns:
            Engine: A SQLAlchemy engine instance.
        """
        with tempfile.NamedTemporaryFile() as tmpfile:
            return create_engine(f"sqlite:///{tmpfile.name}", **self.engine_kwargs)

    def get_session(self) -> Session:
        """Create a new SQLAlchemy session.

        This method creates a new session bound to the engine returned by get_engine().

        Returns:
            Session: A new SQLAlchemy session instance.
        """
        return Session(bind=self.get_engine())

    def reset(self):
        """Reset the connection provider.

        This method disposes of the current engine and clears the engine cache,
        ensuring that a new engine will be created on the next call to get_engine().

        This is used in conjunction with the Snapshot context manager to reset the
        database state between db_mock contexts (especially nested ones).
        """
        self.get_engine().dispose()
        self.get_engine.cache_clear()
