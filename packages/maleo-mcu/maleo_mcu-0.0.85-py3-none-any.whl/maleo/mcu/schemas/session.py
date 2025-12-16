from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, Self, TypeVar, overload
from uuid import UUID
from nexo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from nexo.schemas.document import (
    PDFDocument,
    DocumentMixin,
    OptHomogenousDocumentsMixin,
)
from nexo.schemas.error.enums import ErrorCode
from nexo.schemas.mixins.filter import convert as convert_filter
from nexo.schemas.mixins.identity import (
    IdentifierMixin,
    Ids,
    UUIDs,
    UUIDOrganizationId,
    UUIDOrganizationIds,
    UUIDPatientIds,
    UUIDUserId,
    UUIDUserIds,
)
from nexo.schemas.mixins.sort import convert as convert_sort
from nexo.schemas.operation.enums import ResourceOperationStatusUpdateType
from nexo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from nexo.types.dict import StrToAnyDict
from nexo.types.integer import OptListOfInts
from nexo.types.string import OptStr
from nexo.types.uuid import ListOfUUIDs, OptListOfUUIDs
from ..enums.session import IdentifierType
from ..mixins.common import (
    IncludeURL,
    ClientId,
    ClientIds,
    ParameterIds,
)
from ..mixins.session import SessionTypes, Name, SessionIdentifier
from ..types.session import IdentifierValueType
from .document import GroupCSVDocument


class CreateIndividualParameter(
    IncludeURL,
    OptHomogenousDocumentsMixin[PDFDocument],
    UUIDPatientIds[ListOfUUIDs],
    ParameterIds[OptListOfUUIDs],
    Name[OptStr],
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
):
    name: Annotated[
        OptStr, Field(None, description="Session's name", max_length=250)
    ] = None

    @classmethod
    def _validate_checkup_data(
        cls,
        *,
        patient_ids: ListOfUUIDs,
        documents: list[PDFDocument] | None = None,
    ):
        if len(patient_ids) > 50:
            raise ValueError(
                ErrorCode.BAD_REQUEST,
                "Can not create more than 50 individual MCU at the same time",
            )

        for patient_id in patient_ids:
            pid_prefix = f"{str(patient_id)}_"

            if documents is not None:
                session_documents = [
                    document.filename
                    for document in documents
                    if document.filename.startswith(pid_prefix)
                ]
                if len(session_documents) > 1:
                    raise ValueError(
                        ErrorCode.BAD_REQUEST,
                        f"Found more than one document for patient: '{patient_id}' which are {session_documents}",
                    )

    @classmethod
    def from_form(
        cls,
        *,
        user_id: UUID,
        organization_id: UUID,
        name: OptStr = None,
        parameter_ids: OptListOfUUIDs = None,
        patient_ids: ListOfUUIDs,
        documents: list[PDFDocument] | None = None,
        include_url: bool = False,
    ) -> Self:
        cls._validate_checkup_data(patient_ids=patient_ids, documents=documents)
        return cls(
            user_id=user_id,
            organization_id=organization_id,
            name=name,
            parameter_ids=parameter_ids,
            patient_ids=patient_ids,
            documents=documents,
            include_url=include_url,
        )

    @property
    def checkup_data(self) -> dict[UUID, PDFDocument | None]:
        self._validate_checkup_data(
            patient_ids=self.patient_ids, documents=self.documents
        )
        data: dict[UUID, PDFDocument | None] = {}
        for patient_id in self.patient_ids:
            pid_prefix = f"{str(patient_id)}_"

            # Define document
            if self.documents is None:
                document = None
            else:
                document = next(
                    (
                        doc
                        for doc in self.documents
                        if doc.filename.startswith(pid_prefix)
                    ),
                    None,
                )

            data[patient_id] = document
        return data


class CreateGroupParameter(
    IncludeURL,
    DocumentMixin[GroupCSVDocument],
    ClientId[UUID],
    ParameterIds[OptListOfUUIDs],
    Name[OptStr],
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
):
    name: Annotated[
        OptStr, Field(None, description="Session's name", max_length=250)
    ] = None


AnyCreateParameter = CreateGroupParameter | CreateIndividualParameter


class ReadMultipleParameter(
    IncludeURL,
    ReadPaginatedMultipleParameter,
    ClientIds[OptListOfUUIDs],
    SessionTypes,
    UUIDOrganizationIds[OptListOfUUIDs],
    UUIDUserIds[OptListOfUUIDs],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    ids: Annotated[OptListOfInts, Field(None, description="Ids")] = None
    uuids: Annotated[OptListOfUUIDs, Field(None, description="UUIDs")] = None
    user_ids: Annotated[OptListOfUUIDs, Field(None, description="User's IDs")] = None
    organization_ids: Annotated[
        OptListOfUUIDs, Field(None, description="Organization's IDs")
    ] = None
    client_ids: Annotated[OptListOfUUIDs, Field(None, description="Client's Ids")] = (
        None
    )

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "user_ids",
            "organization_ids",
            "types",
            "client_ids",
            "search",
            "page",
            "limit",
            "use_cache",
            "include_url",
        }

    def to_query_params(self) -> StrToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


class ReadSingleParameter(IncludeURL, BaseReadSingleParameter[SessionIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: SessionIdentifier,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
        include_url: bool = False,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            statuses=statuses,
            use_cache=use_cache,
            include_url=include_url,
        )

    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        include_url: bool = False,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        include_url: bool = False,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        include_url: bool = False,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        include_url: bool = False,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=SessionIdentifier(
                type=identifier_type,
                value=identifier_value,
            ),
            statuses=statuses,
            use_cache=use_cache,
            include_url=include_url,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache"}, exclude_none=True
        )


class FullUpdateData(
    ParameterIds[OptListOfUUIDs],
    Name[str],
):
    pass


class PartialUpdateData(
    ParameterIds[OptListOfUUIDs],
    Name[OptStr],
):
    name: Annotated[
        OptStr, Field(None, description="Session's name", max_length=250)
    ] = None
    parameter_ids: Annotated[
        OptListOfUUIDs, Field(None, description="Parameter's Ids")
    ] = None


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    IncludeURL,
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[SessionIdentifier],
    Generic[UpdateDataT],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        data: UpdateDataT,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        data: UpdateDataT,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        include_url: bool = False,
    ) -> "UpdateParameter":
        return cls(
            identifier=SessionIdentifier(type=identifier_type, value=identifier_value),
            data=data,
            include_url=include_url,
        )


class StatusUpdateParameter(
    IncludeURL,
    BaseStatusUpdateParameter[SessionIdentifier],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        type: ResourceOperationStatusUpdateType,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        type: ResourceOperationStatusUpdateType,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        include_url: bool = False,
    ) -> "StatusUpdateParameter":
        return cls(
            identifier=SessionIdentifier(type=identifier_type, value=identifier_value),
            type=type,
            include_url=include_url,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[SessionIdentifier]):
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.ID], identifier_value: int
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.UUID], identifier_value: UUID
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter": ...
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter":
        return cls(
            identifier=SessionIdentifier(type=identifier_type, value=identifier_value)
        )
