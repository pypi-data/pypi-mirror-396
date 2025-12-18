from datetime import date
from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeVar, overload
from uuid import UUID
from nexo.enums.identity import (
    OptBloodType,
    BloodTypeMixin,
    OptListOfBloodTypes,
    BloodTypesMixin,
    OptRhesus,
    RhesusMixin,
    OptListOfRhesuses,
    RhesusesMixin,
    Gender,
    OptGender,
    GenderMixin,
    OptListOfGenders,
    GendersMixin,
)
from nexo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from nexo.schemas.mixins.filter import convert as convert_filter
from nexo.schemas.mixins.identity import (
    IdentifierMixin,
    Ids,
    UUIDs,
    FullNames,
    DateOfBirth,
    IntUserId,
    IntUserIds,
    IntOrganizationId,
    IntOrganizationIds,
)
from nexo.schemas.mixins.sort import convert as convert_sort
from nexo.schemas.operation.enums import ResourceOperationStatusUpdateType
from nexo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from nexo.types.datetime import OptDate
from nexo.types.dict import StrToAnyDict
from nexo.types.integer import OptListOfInts
from nexo.types.string import OptStr, OptListOfStrs
from nexo.types.uuid import OptListOfUUIDs
from ..enums.patient import IdentifierType, OptListOfExpandableFields
from ..mixins.common import IdCard, FullName, PlaceOfBirth
from ..mixins.patient import PatientIdentity, PatientIdentifier, Expand
from ..types.patient import IdentifierValueType


class StandardCreateData(
    RhesusMixin[OptRhesus],
    BloodTypeMixin[OptBloodType],
    GenderMixin[Gender],
    DateOfBirth[date],
    PlaceOfBirth[OptStr],
    FullName[str],
    PatientIdentity,
):
    pass


class FullCreateData(
    StandardCreateData,
    IntOrganizationId[int],
):
    pass


class CreateParameter(Expand, FullCreateData, IntUserId[int]):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameter,
    RhesusesMixin[OptListOfRhesuses],
    BloodTypesMixin[OptListOfBloodTypes],
    GendersMixin[OptListOfGenders],
    FullNames[OptListOfStrs],
    IntOrganizationIds[OptListOfInts],
    IntUserIds[OptListOfInts],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    ids: Annotated[OptListOfInts, Field(None, description="Ids")] = None
    uuids: Annotated[OptListOfUUIDs, Field(None, description="UUIDs")] = None
    user_ids: Annotated[OptListOfInts, Field(None, description="User's IDs")] = None
    organization_ids: Annotated[
        OptListOfInts, Field(None, description="Organization's IDs")
    ] = None
    full_names: Annotated[OptListOfStrs, Field(None, description="Full Names")] = None
    genders: Annotated[OptListOfGenders, Field(None, description="Genders")] = None
    blood_types: Annotated[
        OptListOfBloodTypes, Field(None, description="Blood Types")
    ] = None
    rhesuses: Annotated[OptListOfRhesuses, Field(None, description="Rhesuses")] = None

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "user_ids",
            "organization_ids",
            "full_names",
            "genders",
            "blood_types",
            "rhesuses",
            "search",
            "page",
            "limit",
            "use_cache",
            "expand",
        }

    def to_query_params(self) -> StrToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


class ReadSingleParameter(Expand, BaseReadSingleParameter[PatientIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: PatientIdentifier,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier, statuses=statuses, use_cache=use_cache, expand=expand
        )

    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=PatientIdentifier(
                type=identifier_type,
                value=identifier_value,
            ),
            statuses=statuses,
            use_cache=use_cache,
            expand=expand,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache", "expand"}, exclude_none=True
        )


class FullUpdateData(
    RhesusMixin[OptRhesus],
    BloodTypeMixin[OptBloodType],
    GenderMixin[Gender],
    DateOfBirth[date],
    PlaceOfBirth[OptStr],
    FullName[str],
    PatientIdentity,
    IdCard[OptStr],
):
    pass


class PartialUpdateData(
    RhesusMixin[OptRhesus],
    BloodTypeMixin[OptBloodType],
    GenderMixin[OptGender],
    DateOfBirth[OptDate],
    PlaceOfBirth[OptStr],
    FullName[OptStr],
    PatientIdentity,
    IdCard[OptStr],
):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    Expand,
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[PatientIdentifier],
    Generic[UpdateDataT],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
    ) -> "UpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
    ) -> "UpdateParameter":
        return cls(
            identifier=PatientIdentifier(type=identifier_type, value=identifier_value),
            data=data,
            expand=expand,
        )


class StatusUpdateParameter(
    Expand,
    BaseStatusUpdateParameter[PatientIdentifier],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
    ) -> "StatusUpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
    ) -> "StatusUpdateParameter":
        return cls(
            identifier=PatientIdentifier(type=identifier_type, value=identifier_value),
            type=type,
            expand=expand,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[PatientIdentifier]):
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
            identifier=PatientIdentifier(type=identifier_type, value=identifier_value)
        )
