import asyncio
from typing import TYPE_CHECKING

from .snapshot import Snapshot

if TYPE_CHECKING:
    from sqlalchemy import Engine

    from .async_connection_provider import MockAsyncConnectionProvider


class AsyncSnapshot(Snapshot):
    if TYPE_CHECKING:
        engine: "Engine"
        tmpfile_name: str
        connection_provider: "MockAsyncConnectionProvider"

    def __init__(self, connection_provider: "MockAsyncConnectionProvider"):
        """Initialize a new Snapshot instance.

        Args:
            connection_provider (MockConnectionProvider): The connection provider for the database.
        """
        self.connection_provider = connection_provider
        super().__init__(connection_provider)

    async def __aenter__(self):
        """Enter the context manager, creating a snapshot of the current database state.

        This method creates a temporary file and dumps the current database state into it.

        Returns:
            Snapshot: The Snapshot instance.
        """
        return await asyncio.to_thread(self.__enter__)

    async def __aexit__(self, exc_type, exc_value, traceback):
        """Exit the context manager, restoring the database to the snapshotted state.

        This method resets the connection provider and restores the database state
        from the temporary file created in __enter__.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
            exc_value: The instance of the exception that caused the context to be exited.
            traceback: A traceback object encoding the stack trace.
        """
        await self.connection_provider.async_reset()
        return await asyncio.to_thread(self.__exit__, exc_type, exc_value, traceback)
