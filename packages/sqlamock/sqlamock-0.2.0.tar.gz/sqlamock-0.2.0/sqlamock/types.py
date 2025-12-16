from typing import TypeVar

from sqlalchemy.orm import DeclarativeBase

BaseType = TypeVar("BaseType", bound=DeclarativeBase)
