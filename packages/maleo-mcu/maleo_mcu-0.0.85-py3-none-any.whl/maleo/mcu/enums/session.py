from enum import StrEnum
from typing import TypeVar
from nexo.types.string import ListOfStrs


class Granularity(StrEnum):
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def column(self) -> str:
        return self.value


class SessionType(StrEnum):
    GROUP = "group"
    INDIVIDUAL = "individual"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


OptSessionType = SessionType | None
OptSessionTypeT = TypeVar("OptSessionTypeT", bound=OptSessionType)
ListOfSessionTypes = list[SessionType]
OptListOfSessionTypes = ListOfSessionTypes | None
OptListOfSessionTypesT = TypeVar("OptListOfSessionTypesT", bound=OptListOfSessionTypes)
