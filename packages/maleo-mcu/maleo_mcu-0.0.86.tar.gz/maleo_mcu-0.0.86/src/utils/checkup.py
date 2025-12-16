from typing import Literal, Type, overload
from ..schemas.common import (
    StandardCheckupSchema,
    FullCheckupSchema,
    AnyCheckupSchemaType,
)
from ..enums.checkup import Granularity


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardCheckupSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullCheckupSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyCheckupSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyCheckupSchemaType:
    if granularity is Granularity.STANDARD:
        return StandardCheckupSchema
    elif granularity is Granularity.FULL:
        return FullCheckupSchema
