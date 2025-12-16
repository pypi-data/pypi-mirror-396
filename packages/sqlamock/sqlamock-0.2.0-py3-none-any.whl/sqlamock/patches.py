from contextlib import ExitStack
from threading import Lock
from typing import TYPE_CHECKING
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.sqltypes import Enum

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import Self


def mock_enum():
    original = Enum._object_value_for_elem

    def _(*args, **kwargs):
        try:
            return original(*args, **kwargs)
        except LookupError as e:
            raise IntegrityError(
                (
                    "(psycopg.errors.InvalidTextRepresentation) "
                    f"invalid input value for enum '{kwargs.get('column_name', 'unknown_enum')}': '{kwargs.get('value', 'unknown_value')}'\n"
                    "DETAIL:  The provided value is not an existing member of the enum set."
                ),
                params=None,
                orig=e,
            ) from e

    return patch.object(Enum, "_object_value_for_elem", _)


class Patches(ExitStack):
    """Manages SQLAlchemy patches and other db related patches for testing within a db_mock context.

    It can handle nested contexts safely using an internal lock and counter, applying patches only once when the first context is entered,
    and restoring them when the final context is exited.

    Attributes:
        patches (list[AbstractContextManager]): A list of additional patches added by the user.
        counter (int): Tracks the number of active contexts to control the application and restoration of patches.
    """

    if TYPE_CHECKING:
        _lock: Lock
        patches: list[AbstractContextManager]
        counter: int

    def __init__(self, *args, **kwargs):
        """Initializes the Patches context manager.

        This sets up the necessary lock, initializes the patch list and counter, and
        inherits from `ExitStack` for efficient context management.
        """
        super().__init__(*args, **kwargs)
        self._lock = Lock()
        self.patches = [mock_enum()]
        self.counter = 0

    def add_patch(self, patch: "AbstractContextManager"):
        """Adds an additional patch to be applied within the db_mock context.

        This method allows adding extra patches, which will be applied along with
        `mock_enum` when the context is entered. This is useful for any custom patches
        needed in conjunction with the main SQLAlchemy patches. This is defined at the session
        scope.

        Args:
            patch (AbstractContextManager): The patch context manager to be added.
        """
        self.patches.append(patch)

    def __enter__(self) -> "Self":
        """db_mock manages opening and closing Patches context, to apply the patches alongside the db_mock context.

        If this is the first context being entered (counter is 0), it applies all patches. The counter increments with each
        nested context to count the number of active contexts.

        Returns:
            Patches: The current instance of Patches, with patches applied.
        """
        with self._lock:
            if self.counter == 0:
                for patch in self.patches:
                    self.enter_context(patch)

            self.counter += 1

        return super().__enter__()

    def __exit__(self, *args, **kwargs) -> None:
        """Counts down the number of active contexts, restoring patches when the last nested context exits."""
        with self._lock:
            self.counter -= 1
            if self.counter == 0:
                super().__exit__(*args, **kwargs)
