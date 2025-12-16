from datetime import date
from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Generic, Self, Type, TypeVar
from uuid import UUID
from nexo.enums.identity import (
    OptRhesus,
    RhesusMixin,
    OptBloodType,
    BloodTypeMixin,
    Gender,
    GenderMixin,
)
from nexo.schemas.document import DocumentName, DocumentURL
from nexo.schemas.mixins.identity import (
    DataIdentifier,
    UUIDUserId,
    UUIDOrganizationId,
    DateOfBirth,
)
from nexo.types.integer import OptInt
from nexo.types.string import OptStr, OptListOfStrs
from ..enums.checkup import (
    CheckupType as CheckupTypeEnum,
    OptCheckupType,
    CheckupStatus as CheckupStatusEnum,
)
from ..enums.examination import OptExaminationStatus
from ..enums.finding_parameter import Criteria as CriteriaEnum
from ..enums.finding import Logic as LogicEnum
from ..enums.parameter import (
    ParameterGroup,
    ValueType as ValueTypeEnum,
)
from ..enums.session import SessionType as SessionTypeEnum
from ..mixins.ascvd_risk import (
    AgeRange,
    AgeRangeMixin,
    Diabetes,
    Smoker,
    TotalCholesterolRange,
    TotalCholesterolRangeMixin,
    SystolicBloodPressureRange,
    SystolicBloodPressureRangeMixin,
    Score,
)
from ..mixins.checkup_ascvd_risk import Recommendation as CheckupASCVDRiskRecommendation
from ..mixins.checkup_finding import Recommendation as CheckupFindingRecommendation
from ..mixins.checkup import (
    CheckupType,
    CheckupDate,
    CheckupStatus,
    RadiologyRecordId,
    SummaryMixin,
)
from ..mixins.client import Name as ClientName
from ..mixins.examination import (
    OrganExaminations,
    ExaminationStatus,
    Value,
    Unit as ExaminationUnit,
)
from ..mixins.finding_parameter import Criteria, Weight
from ..mixins.finding import (
    Name as FindingName,
    Aliases as FindingAliases,
    Recommendation as FindingRecommendation,
    Logic,
)
from ..mixins.parameter import (
    _validate_value_type_and_options,
    Group,
    IsMandatory,
    Name as ParameterName,
    Aliases,
    ValueType,
    Options,
    IsNullable,
    Unit as ParameterUnit,
)
from ..mixins.patient import IdCard, FullName, PlaceOfBirth
from ..mixins.rule import RuleData
from ..mixins.session import SessionType, Name as SessionName


class ASCVDRiskSchema(
    Score[int],
    SystolicBloodPressureRangeMixin[SystolicBloodPressureRange],
    TotalCholesterolRangeMixin[TotalCholesterolRange],
    Smoker[bool],
    Diabetes[bool],
    AgeRangeMixin[AgeRange],
    GenderMixin[Gender],
    DataIdentifier,
):
    pass


ListOfASCVDRiskSchemas = list[ASCVDRiskSchema]


class ASCVDRiskSchemaMixin(BaseModel):
    ascvd_risk: Annotated[ASCVDRiskSchema, Field(..., description="ASCVD Risk")]


class SimpleASCVDRiskSchemaMixin(BaseModel):
    risk: Annotated[ASCVDRiskSchema, Field(..., description="ASCVD Risk")]


class ClientSchema(
    ClientName[str],
    UUIDOrganizationId[UUID],
    DataIdentifier,
):
    pass


OptClientSchema = ClientSchema | None
OptClientSchemaT = TypeVar("OptClientSchemaT", bound=OptClientSchema)


class ClientSchemaMixin(BaseModel, Generic[OptClientSchemaT]):
    client: Annotated[OptClientSchemaT, Field(..., description="Client")]


class PatientSchema(
    RhesusMixin[OptRhesus],
    BloodTypeMixin[OptBloodType],
    GenderMixin[Gender],
    DateOfBirth[date],
    PlaceOfBirth[OptStr],
    FullName[str],
    IdCard[str],
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
    DataIdentifier,
):

    pass


class PatientSchemaMixin(BaseModel):
    patient: Annotated[PatientSchema, Field(..., description="Patient")]


class StandardParameterSchema(
    ParameterUnit[OptStr],
    IsNullable[bool],
    Options[OptListOfStrs],
    ValueType[ValueTypeEnum],
    Aliases[OptListOfStrs],
    ParameterName[str],
    Group[ParameterGroup],
    IsMandatory[bool],
    DataIdentifier,
):
    @model_validator(mode="after")
    def validate_value_type_and_options(self) -> Self:
        _validate_value_type_and_options(self.value_type, self.options)
        return self


OptStandardParameterSchema = StandardParameterSchema | None
ListOfStandardParameterSchemas = list[StandardParameterSchema]


class StandardParameterSchemaMixin(BaseModel):
    parameter: Annotated[StandardParameterSchema, Field(..., description="Parameter")]


class StandardRuleSchema(
    RuleData,
    DataIdentifier,
):
    pass


OptStandardRuleSchema = StandardRuleSchema | None
ListOfStandardRuleSchemas = list[StandardRuleSchema]


class StandardRuleSchemasMixin(BaseModel):
    rules: Annotated[
        ListOfStandardRuleSchemas,
        Field(ListOfStandardRuleSchemas(), description="Rules"),
    ] = ListOfStandardRuleSchemas()


class FullParameterSchema(
    StandardRuleSchemasMixin,
    StandardParameterSchema,
):
    pass


AnyParameterSchemaType = Type[StandardParameterSchema] | Type[FullParameterSchema]
AnyParameterSchema = StandardParameterSchema | FullParameterSchema
AnyParameterSchemaT = TypeVar("AnyParameterSchemaT", bound=AnyParameterSchema)
OptAnyParameterSchema = AnyParameterSchema | None
OptAnyParameterSchemaT = TypeVar("OptAnyParameterSchemaT", bound=OptAnyParameterSchema)


class ParameterSchemaMixin(BaseModel, Generic[OptAnyParameterSchemaT]):
    parameter: Annotated[OptAnyParameterSchemaT, Field(..., description="Parameter")]


class FullRuleSchema(
    RuleData,
    StandardParameterSchemaMixin,
    DataIdentifier,
):
    pass


AnyRuleSchemaType = Type[StandardRuleSchema] | Type[FullRuleSchema]
AnyRuleSchema = StandardRuleSchema | FullRuleSchema
AnyRuleSchemaT = TypeVar("AnyRuleSchemaT", bound=AnyRuleSchema)
OptAnyRuleSchema = AnyRuleSchema | None
OptAnyRuleSchemaT = TypeVar("OptAnyRuleSchemaT", bound=OptAnyRuleSchema)


class RuleSchemaMixin(BaseModel, Generic[OptAnyRuleSchemaT]):
    rule: Annotated[OptAnyRuleSchemaT, Field(..., description="Rule")]


class StandardFindingSchema(
    Logic[LogicEnum],
    FindingRecommendation[str],
    FindingAliases[OptListOfStrs],
    FindingName[str],
    DataIdentifier,
):
    pass


ListOfStandardFindingSchemas = list[StandardFindingSchema]


class FindingParameterSchema(
    Weight[OptInt],
    Criteria[CriteriaEnum],
    StandardParameterSchemaMixin,
    DataIdentifier,
):
    pass


ListOfFindingParameterSchemas = list[FindingParameterSchema]


class FindingParameterSchemasMixin(BaseModel):
    parameters: Annotated[
        ListOfFindingParameterSchemas,
        Field(ListOfFindingParameterSchemas(), description="Finding Parameters"),
    ] = ListOfFindingParameterSchemas()


class FullFindingSchema(
    FindingParameterSchemasMixin,
    StandardFindingSchema,
):
    pass


ListOfFullFindingSchemas = list[FullFindingSchema]


AnyFindingSchemaType = Type[StandardFindingSchema] | Type[FullFindingSchema]
AnyFindingSchema = StandardFindingSchema | FullFindingSchema
AnyFindingSchemaT = TypeVar("AnyFindingSchemaT", bound=AnyFindingSchema)
OptAnyFindingSchema = AnyFindingSchema | None
OptAnyFindingSchemaT = TypeVar("OptAnyFindingSchemaT", bound=OptAnyFindingSchema)


class FindingSchemaMixin(BaseModel, Generic[OptAnyFindingSchemaT]):
    finding: Annotated[OptAnyFindingSchemaT, Field(..., description="Finding")]


class LabExtractedExaminationData(BaseModel):
    parameter: Annotated[str, Field(..., description="Parameter's name")]
    value: Annotated[str, Field(..., description="Parameter's value")]
    unit: Annotated[str, Field(..., description="Parameter's unit")]


ListOfLabExtractedExaminationData = list[LabExtractedExaminationData]


class BareExaminationSchema(
    ExaminationUnit,
    Value,
    ParameterSchemaMixin[OptAnyParameterSchemaT],
    Generic[OptAnyParameterSchemaT],
):
    pass


class RawExaminationSchema(
    BareExaminationSchema[FullParameterSchema],
):
    pass


OptRawExaminationSchema = RawExaminationSchema | None
ListOfRawExaminationSchemas = list[RawExaminationSchema]


class BaseExaminationSchema(
    RuleSchemaMixin[OptStandardRuleSchema],
    ExaminationStatus[OptExaminationStatus],
    BareExaminationSchema[StandardParameterSchema],
):
    pass


class ExaminationSchema(
    BaseExaminationSchema,
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
    DataIdentifier,
):
    pass


ListOfExaminationSchemas = list[ExaminationSchema]


class ExaminationSchemasMixin(BaseModel):
    examinations: Annotated[
        ListOfExaminationSchemas,
        Field(ListOfExaminationSchemas(), description="Examinations"),
    ] = ListOfExaminationSchemas()


class CheckupFindingSchema(
    CheckupFindingRecommendation[str],
    FindingSchemaMixin[StandardFindingSchema],
    DataIdentifier,
):
    pass


ListOfCheckupFindingSchemas = list[CheckupFindingSchema]


class CheckupFindingSchemasMixin(BaseModel):
    findings: Annotated[
        ListOfCheckupFindingSchemas,
        Field(ListOfCheckupFindingSchemas(), description="Findings"),
    ] = ListOfCheckupFindingSchemas()


class CheckupASCVDRiskSchema(
    CheckupASCVDRiskRecommendation,
    ASCVDRiskSchemaMixin,
):
    pass


OptCheckupASCVDRiskSchema = CheckupASCVDRiskSchema | None


class CheckupASCVDRiskSchemaMixin(BaseModel):
    ascvd_risk: Annotated[
        OptCheckupASCVDRiskSchema, Field(None, description="ASCVD Risk")
    ] = None


class CheckupAnalysis(
    SummaryMixin,
    CheckupASCVDRiskSchemaMixin,
    CheckupFindingSchemasMixin,
    OrganExaminations,
):
    pass


class CheckupAnalysisMixin(BaseModel):
    analysis: Annotated[CheckupAnalysis, Field(..., description="Analysis")]


class StandardCheckupSchema(
    SummaryMixin,
    CheckupASCVDRiskSchemaMixin,
    CheckupFindingSchemasMixin,
    ExaminationSchemasMixin,
    OrganExaminations,
    RadiologyRecordId,
    PatientSchemaMixin,
    DocumentURL[OptStr],
    DocumentName[OptStr],
    CheckupStatus[CheckupStatusEnum],
    CheckupDate[date],
    ClientSchemaMixin[OptClientSchema],
    CheckupType[OptCheckupType],
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
    DataIdentifier,
):
    document_name: Annotated[OptStr, Field(None, description="Document's name")] = None
    document_url: Annotated[OptStr, Field(None, description="Document's URL")] = None

    @model_validator(mode="after")
    def validate_type_client(self) -> Self:
        if self.type is not None:
            if self.type is CheckupTypeEnum.GROUP:
                if self.client is None:
                    raise ValueError("Client can not be None for Group Checkup")
            elif self.type is CheckupTypeEnum.INDIVIDUAL:
                if self.client is not None:
                    raise ValueError("Client must be None for Individual Checkup")
        return self


ListOfStandardCheckupSchemas = list[StandardCheckupSchema]


class StandardCheckupSchemasMixin(BaseModel):
    checkups: Annotated[
        ListOfStandardCheckupSchemas,
        Field(ListOfStandardCheckupSchemas(), description="Checkups"),
    ] = ListOfStandardCheckupSchemas()


class StandardSessionSchema(
    SessionName[str],
    ClientSchemaMixin[OptClientSchema],
    SessionType[SessionTypeEnum],
    UUIDOrganizationId[UUID],
    UUIDUserId[UUID],
    DataIdentifier,
):
    @model_validator(mode="after")
    def validate_type_client(self) -> Self:
        if self.type is SessionTypeEnum.GROUP:
            if self.client is None:
                raise ValueError("Client can not be None for group MCU")
        elif self.type is SessionTypeEnum.INDIVIDUAL:
            if self.client is not None:
                raise ValueError("Client must be None for individual MCU")
        return self


OptStandardSessionSchema = StandardSessionSchema | None


class StandardSessionSchemaMixin(BaseModel):
    session: Annotated[OptStandardSessionSchema, Field(None, description="Session")] = (
        None
    )


class FullCheckupSchema(StandardSessionSchemaMixin, StandardCheckupSchema):
    pass


AnyCheckupSchemaType = Type[StandardCheckupSchema] | Type[FullCheckupSchema]
AnyCheckupSchema = StandardCheckupSchema | FullCheckupSchema


class FullSessionSchema(StandardCheckupSchemasMixin, StandardSessionSchema):
    pass


AnySessionSchemaType = Type[StandardSessionSchema] | Type[FullSessionSchema]
AnySessionSchema = StandardSessionSchema | FullSessionSchema
