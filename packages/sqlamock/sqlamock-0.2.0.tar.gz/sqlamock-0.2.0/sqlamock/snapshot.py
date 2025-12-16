import tempfile
from contextlib import ExitStack
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import Engine

    from .connection_provider import ConnectionProvider


class Snapshot(ExitStack):
    """ContextManager that helps separate the scopes of database mocked data contexts.

    This class extends ExitStack to provide a mechanism for capturing and restoring
    the state of a database context. It is opened at the start of a db_mock context to
    create a snapshot of the pre-existing database state. When the db_mock context is exited,
    the snapshot is restored, effectively resetting anything that happened during the db_mock context.

    This is a critical part of teardown and maintaining deterministic testing state. This can only be used
    as a context manager within a db_mock context.

    Not meant for public use.

    Attributes:
           engine (Engine): The recyclable engine specific to the snapshot context.
           tmpfile_name (str): The name of the temporary file used to store the snapshot.
           connection_provider (MockConnectionProvider): The connection provider for the database.
    """

    if TYPE_CHECKING:
        engine: "Engine"
        tmpfile_name: str
        connection_provider: "ConnectionProvider"

    def __init__(self, connection_provider: "ConnectionProvider"):
        """Initialize a new Snapshot instance.

        Args:
            connection_provider (MockConnectionProvider): The connection provider for the database.
        """
        self.connection_provider = connection_provider
        super().__init__()

    def __enter__(self):
        """Enter the context manager, creating a snapshot of the current database state.

        This method creates a temporary file and dumps the current database state into it.

        Returns:
            Snapshot: The Snapshot instance.
        """
        tmpfile = tempfile.NamedTemporaryFile()
        self.tmpfile_name = self.enter_context(tmpfile).name
        with self.connection_provider.get_engine().connect() as conn:
            with open(self.tmpfile_name, "w") as f:
                for line in conn.connection.iterdump():
                    f.write(f"{line}\n")
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager, restoring the database to the snapshotted state.

        This method resets the connection provider and restores the database state
        from the temporary file created in __enter__.

        Args:
            exc_type: The type of the exception that caused the context to be exited.
            exc_value: The instance of the exception that caused the context to be exited.
            traceback: A traceback object encoding the stack trace.
        """
        self.connection_provider.reset()
        with self.connection_provider.get_engine().connect() as conn:
            with open(self.tmpfile_name) as f:
                conn.connection.executescript(f.read())

        return super().__exit__(exc_type, exc_value, traceback)
