from pydantic import BaseModel, Field
from typing import Annotated, Generic
from nexo.types.uuid import OptUUIDT, OptListOfUUIDsT


class IncludeURL(BaseModel):
    include_url: Annotated[bool, Field(False, description="Whether to include URL")] = (
        False
    )


class ClientId(BaseModel, Generic[OptUUIDT]):
    client_id: Annotated[OptUUIDT, Field(..., description="Client's Id")]


class ClientIds(BaseModel, Generic[OptListOfUUIDsT]):
    client_ids: Annotated[OptListOfUUIDsT, Field(..., description="Client's Ids")]


class SessionId(BaseModel, Generic[OptUUIDT]):
    session_id: Annotated[OptUUIDT, Field(..., description="Session's Id")]


class SessionIds(BaseModel, Generic[OptListOfUUIDsT]):
    session_ids: Annotated[OptListOfUUIDsT, Field(..., description="Session's Ids")]


class ParameterIds(BaseModel, Generic[OptListOfUUIDsT]):
    parameter_ids: Annotated[OptListOfUUIDsT, Field(..., description="Parameter's Ids")]
