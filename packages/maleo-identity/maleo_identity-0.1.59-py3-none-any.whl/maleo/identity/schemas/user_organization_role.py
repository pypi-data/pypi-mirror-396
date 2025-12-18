from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeVar, overload
from uuid import UUID
from nexo.enums.organization import (
    OrganizationRole,
    OptOrganizationRole,
    FullOrganizationRoleMixin,
    OptListOfOrganizationRoles,
    FullOrganizationRolesMixin,
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
from nexo.types.dict import StrToAnyDict
from nexo.types.integer import OptInt, OptListOfInts
from nexo.types.uuid import OptListOfUUIDs
from ..enums.user_organization_role import IdentifierType, OptListOfExpandableFields
from ..mixins.user_organization_role import Expand, UserOrganizationRoleIdentifier
from ..types.user_organization_role import CompositeIdentifierType, IdentifierValueType


class BaseCreateData(FullOrganizationRoleMixin[OrganizationRole]):
    pass


class CreateFromOrganizationData(
    FullOrganizationRoleMixin[OrganizationRole],
    IntUserId[int],
):
    pass


class CreateFromUserData(
    FullOrganizationRoleMixin[OrganizationRole],
    IntOrganizationId[int],
):
    pass


class FullCreateData(
    FullOrganizationRoleMixin[OrganizationRole],
    IntOrganizationId[int],
    IntUserId[int],
):
    pass


class CreateParameter(
    Expand,
    FullCreateData,
):
    pass


class ReadMultipleParameter(
    Expand,
    ReadPaginatedMultipleParameter,
    FullOrganizationRolesMixin[OptListOfOrganizationRoles],
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
    organization_roles: Annotated[
        OptListOfOrganizationRoles, Field(None, description="Organization Roles")
    ] = None

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "user_ids",
            "organization_ids",
            "organization_roles",
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


class ReadSingleParameter(
    Expand, BaseReadSingleParameter[UserOrganizationRoleIdentifier]
):
    @classmethod
    def from_identifier(
        cls,
        identifier: UserOrganizationRoleIdentifier,
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
        identifier_type: Literal[IdentifierType.COMPOSITE],
        identifier_value: CompositeIdentifierType,
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
            identifier=UserOrganizationRoleIdentifier(
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
    FullOrganizationRoleMixin[OrganizationRole],
    IntOrganizationId[int],
    IntUserId[int],
):
    pass


class PartialUpdateData(
    FullOrganizationRoleMixin[OptOrganizationRole],
    IntOrganizationId[OptInt],
    IntUserId[OptInt],
):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    Expand,
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[UserOrganizationRoleIdentifier],
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
        identifier_type: Literal[IdentifierType.COMPOSITE],
        identifier_value: CompositeIdentifierType,
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
            identifier=UserOrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            ),
            data=data,
            expand=expand,
        )


class StatusUpdateParameter(
    Expand,
    BaseStatusUpdateParameter[UserOrganizationRoleIdentifier],
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
        identifier_type: Literal[IdentifierType.COMPOSITE],
        identifier_value: CompositeIdentifierType,
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
            identifier=UserOrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            ),
            type=type,
            expand=expand,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[UserOrganizationRoleIdentifier]):
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
        identifier_type: Literal[IdentifierType.COMPOSITE],
        identifier_value: CompositeIdentifierType,
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
            identifier=UserOrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            )
        )
