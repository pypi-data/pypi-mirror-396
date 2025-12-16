from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier, Name as BaseName
from nexo.types.string import OptStrT
from ..enums.session import (
    IdentifierType,
    OptSessionTypeT,
    OptListOfSessionTypes,
)
from ..types.session import IdentifierValueType


class SessionType(BaseModel, Generic[OptSessionTypeT]):
    type: Annotated[OptSessionTypeT, Field(..., description="Session's type")]


class SessionTypes(BaseModel):
    types: Annotated[
        OptListOfSessionTypes, Field(None, description="Session's types")
    ] = None


class Name(BaseName, Generic[OptStrT]):
    name: Annotated[OptStrT, Field(..., description="Session's name", max_length=250)]


class SessionIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdSessionIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDSessionIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


AnySessionIdentifier = SessionIdentifier | IdSessionIdentifier | UUIDSessionIdentifier


def is_id_identifier(
    identifier: AnySessionIdentifier,
) -> TypeGuard[IdSessionIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnySessionIdentifier,
) -> TypeGuard[UUIDSessionIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)
