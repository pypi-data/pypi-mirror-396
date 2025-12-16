from typing import Literal, Type, overload
from ..schemas.common import (
    StandardSessionSchema,
    FullSessionSchema,
    AnySessionSchemaType,
)
from ..enums.session import Granularity


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardSessionSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullSessionSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnySessionSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnySessionSchemaType:
    if granularity is Granularity.STANDARD:
        return StandardSessionSchema
    elif granularity is Granularity.FULL:
        return FullSessionSchema
