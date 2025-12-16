import asyncio
from functools import lru_cache
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from sqlamock.connection_provider import MockConnectionProvider


class MockAsyncConnectionProvider(MockConnectionProvider):
    """A class that provides mock database connections for patching purposes.

    This class creates and manages SQLite in-memory(file) databases, which can be used
    as a lightweight replacement for actual database connections in tests.

    Attributes:
        engine_kwargs (dict): Additional keyword arguments to pass to create_engine.
    """

    if TYPE_CHECKING:
        engine_kwargs: dict

    def __init__(self, engine_kwargs: dict | None = None):
        """Initialize a new MockAsyncConnectionProvider instance.

        Args:
            engine_kwargs (dict | None): Additional keyword arguments to pass to create_async_engine.
                                         If None, an empty dict will be used.
        """
        self.engine_kwargs = engine_kwargs or {}

    @lru_cache  # noqa: B019
    def get_async_engine(self) -> AsyncEngine:
        """Get or create a SQLAlchemy async engine instance.

        Returns:
            AsyncEngine: A SQLAlchemy async engine instance.
        """
        engine = self.get_engine()
        return create_async_engine(
            engine.url.set(drivername="sqlite+aiosqlite"),
            **self.engine_kwargs,
        )

    def get_async_session(self) -> AsyncSession:
        """Create a new SQLAlchemy async session.

        Returns:
            AsyncSession: A new SQLAlchemy async session instance.
        """
        return AsyncSession(bind=self.get_async_engine())

    async def async_reset(self):
        """Reset the connection provider.

        This method disposes of the current engine and clears the engine cache,
        ensuring that a new engine will be created on the next call to get_engine().

        This is used in conjunction with the Snapshot context manager to reset the
        database state between db_mock contexts (especially nested ones).
        """
        await asyncio.to_thread(self.reset)
        await self.get_async_engine().dispose()
        self.get_async_engine.cache_clear()
