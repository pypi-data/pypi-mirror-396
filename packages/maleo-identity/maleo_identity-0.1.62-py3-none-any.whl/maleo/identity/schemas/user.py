from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Generic, Literal, Self, TypeVar, overload
from uuid import UUID
from nexo.enums.status import (
    ListOfDataStatuses,
    FULL_DATA_STATUSES,
)
from nexo.enums.user import (
    UserType,
    OptUserType,
    FullUserTypeMixin,
    OptListOfUserTypes,
    FullUserTypesMixin,
)
from nexo.schemas.error.enums import ErrorCode
from nexo.schemas.mixins.filter import convert as convert_filter
from nexo.schemas.mixins.identity import (
    IdentifierMixin,
    Ids,
    UUIDs,
    IntOrganizationId,
    IntOrganizationIds,
)
from nexo.schemas.mixins.parameter import IncludeURL
from nexo.schemas.mixins.sort import convert as convert_sort
from nexo.schemas.operation.enums import ResourceOperationStatusUpdateType
from nexo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from nexo.types.dict import StrToAnyDict
from nexo.types.integer import OptInt, OptListOfInts
from nexo.types.string import OptStr, OptListOfStrs
from nexo.types.uuid import OptListOfUUIDs
from ..enums.user import IdentifierType, OptListOfExpandableFields
from ..mixins.user import (
    Username,
    Usernames,
    Email,
    Emails,
    Phone,
    Phones,
    Password,
    Expand,
    UserIdentifier,
)
from ..types.user import IdentifierValueType


class SimpleCreateData(
    Password,
    Phone[str],
    Email[str],
    Username[str],
    FullUserTypeMixin[UserType],
):
    pass


class FullCreateData(
    SimpleCreateData,
    IntOrganizationId[OptInt],
):
    pass


class CreateParameter(Expand, FullCreateData):
    pass


class ReadMultipleParameter(
    IncludeURL,
    Expand,
    ReadPaginatedMultipleParameter,
    Phones[OptListOfStrs],
    Emails[OptListOfStrs],
    Usernames[OptListOfStrs],
    FullUserTypesMixin[OptListOfUserTypes],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
    IntOrganizationIds[OptListOfInts],
):
    organization_ids: Annotated[
        OptListOfInts, Field(None, description="Organization's IDs")
    ] = None
    ids: Annotated[OptListOfInts, Field(None, description="Ids")] = None
    uuids: Annotated[OptListOfUUIDs, Field(None, description="UUIDs")] = None
    user_types: Annotated[OptListOfUserTypes, Field(None, description="User Types")] = (
        None
    )
    usernames: Annotated[OptListOfStrs, Field(None, description="User's Usernames")] = (
        None
    )
    emails: Annotated[OptListOfStrs, Field(None, description="User's Emails")] = None
    phones: Annotated[OptListOfStrs, Field(None, description="User's Phones")] = None

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "organization_ids",
            "ids",
            "uuids",
            "statuses",
            "user_types",
            "usernames",
            "emails",
            "phones",
            "search",
            "page",
            "limit",
            "use_cache",
            "expand",
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


class ReadSingleParameter(IncludeURL, Expand, BaseReadSingleParameter[UserIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: UserIdentifier,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=identifier,
            statuses=statuses,
            use_cache=use_cache,
            expand=expand,
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
        expand: OptListOfExpandableFields = None,
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
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.USERNAME, IdentifierType.EMAIL],
        identifier_value: str,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
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
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = list(FULL_DATA_STATUSES),
        use_cache: bool = True,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=UserIdentifier(
                type=identifier_type,
                value=identifier_value,
            ),
            statuses=statuses,
            use_cache=use_cache,
            expand=expand,
            include_url=include_url,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json",
            include={"statuses", "use_cache", "expand", "include_url"},
            exclude_none=True,
        )


class PasswordUpdateData(BaseModel):
    old_password: Annotated[str, Field(..., description="Old Password", max_length=255)]
    old_confirmation: Annotated[
        str, Field(..., description="Old Password Confirmation", max_length=255)
    ]
    new_password: Annotated[str, Field(..., description="New Password", max_length=255)]

    @model_validator(mode="after")
    def validate_old_and_confirmation(self) -> Self:
        if self.old_password != self.old_confirmation:
            raise ValueError(
                ErrorCode.BAD_REQUEST,
                "Old password must be the same with the confirmation",
            )
        return self


class FullUpdateData(
    Phone[str], Email[str], Username[str], FullUserTypeMixin[UserType]
):
    pass


class PartialUpdateData(
    Phone[OptStr], Email[OptStr], Username[OptStr], FullUserTypeMixin[OptUserType]
):
    pass


UpdateDataT = TypeVar(
    "UpdateDataT", FullUpdateData, PartialUpdateData, PasswordUpdateData
)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    IncludeURL,
    Expand,
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[UserIdentifier],
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
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.USERNAME, IdentifierType.EMAIL],
        identifier_value: str,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "UpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "UpdateParameter":
        return cls(
            identifier=UserIdentifier(type=identifier_type, value=identifier_value),
            data=data,
            expand=expand,
            include_url=include_url,
        )


class StatusUpdateParameter(
    IncludeURL,
    Expand,
    BaseStatusUpdateParameter[UserIdentifier],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.USERNAME, IdentifierType.EMAIL],
        identifier_value: str,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "StatusUpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
        expand: OptListOfExpandableFields = None,
        include_url: bool = False,
    ) -> "StatusUpdateParameter":
        return cls(
            identifier=UserIdentifier(type=identifier_type, value=identifier_value),
            type=type,
            expand=expand,
            include_url=include_url,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[UserIdentifier]):
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
        cls,
        identifier_type: Literal[IdentifierType.USERNAME, IdentifierType.EMAIL],
        identifier_value: str,
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
            identifier=UserIdentifier(type=identifier_type, value=identifier_value)
        )
