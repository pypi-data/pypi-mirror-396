from pydantic import BaseModel, Field
from typing import Annotated, Generic
from nexo.types.uuid import OptUUIDT, OptListOfUUIDsT


class IncludeURL(BaseModel):
    include_url: Annotated[bool, Field(False, description="Whether to include URL")] = (
        False
    )


class CheckupId(BaseModel, Generic[OptUUIDT]):
    checkup_id: Annotated[OptUUIDT, Field(..., description="Checkup's Id")]


class CheckupIds(BaseModel, Generic[OptListOfUUIDsT]):
    checkup_ids: Annotated[OptListOfUUIDsT, Field(..., description="Checkup's Ids")]


class ClientId(BaseModel, Generic[OptUUIDT]):
    client_id: Annotated[OptUUIDT, Field(..., description="Client's Id")]


class ClientIds(BaseModel, Generic[OptListOfUUIDsT]):
    client_ids: Annotated[OptListOfUUIDsT, Field(..., description="Client's Ids")]


class ParameterId(BaseModel, Generic[OptUUIDT]):
    parameter_id: Annotated[OptUUIDT, Field(..., description="Parameter's Id")]


class ParameterIds(BaseModel, Generic[OptListOfUUIDsT]):
    parameter_ids: Annotated[OptListOfUUIDsT, Field(..., description="Parameter's Ids")]
