from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeVar, overload
from uuid import UUID
from nexo.enums.organization import (
    OrganizationRelation,
    SimpleOrganizationRelationMixin,
    OptListOfOrganizationRelations,
    SimpleOrganizationRelationsMixin,
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
    IntSourceId,
    IntSourceIds,
    IntTargetId,
    IntTargetIds,
)
from nexo.schemas.mixins.sort import convert as convert_sort
from nexo.schemas.operation.enums import ResourceOperationStatusUpdateType
from nexo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from nexo.types.boolean import OptBool
from nexo.types.dict import StrToAnyDict
from nexo.types.integer import OptListOfInts
from nexo.types.uuid import OptListOfUUIDs
from ..enums.organization_relation import IdentifierType, OptListOfExpandableFields
from ..mixins.organization_relation import (
    IsBidirectional,
    Meta,
    OrganizationRelationIdentifier,
    Expand,
)
from ..types.organization_relation import CompositeIdentifierType, IdentifierValueType


class BareCreateData(
    Meta,
    IsBidirectional[bool],
):
    is_bidirectional: Annotated[bool, Field(False, description="Is Bidirectional")] = (
        False
    )


class BaseCreateData(
    BareCreateData,
    SimpleOrganizationRelationMixin[OrganizationRelation],
):
    pass


class SimpleCreateData(
    BaseCreateData,
    IntTargetId[int],
):
    pass


class FullCreateData(
    SimpleCreateData,
    IntSourceId[int],
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
    IsBidirectional[OptBool],
    SimpleOrganizationRelationsMixin[OptListOfOrganizationRelations],
    IntTargetIds[OptListOfInts],
    IntSourceIds[OptListOfInts],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    ids: Annotated[OptListOfInts, Field(None, description="Ids")] = None
    uuids: Annotated[OptListOfUUIDs, Field(None, description="UUIDs")] = None
    source_ids: Annotated[OptListOfInts, Field(None, description="Source's IDs")] = None
    target_ids: Annotated[OptListOfInts, Field(None, description="Target's IDs")] = None
    relations: Annotated[
        OptListOfOrganizationRelations,
        Field(None, description="Organization Relations"),
    ] = None
    is_bidirectional: Annotated[
        OptBool, Field(None, description="Whether is bidirectional")
    ] = None

    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "source_ids",
            "target_ids",
            "is_bidirectional",
            "relations",
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
    Expand, BaseReadSingleParameter[OrganizationRelationIdentifier]
):
    @classmethod
    def from_identifier(
        cls,
        identifier: OrganizationRelationIdentifier,
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
            identifier=OrganizationRelationIdentifier(
                type=identifier_type, value=identifier_value
            ),
            statuses=statuses,
            use_cache=use_cache,
            expand=expand,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache", "expand"}, exclude_none=True
        )


class FullUpdateData(Meta, IsBidirectional[bool]):
    is_bidirectional: Annotated[bool, Field(..., description="Is Bidirectional")]


class PartialUpdateData(Meta, IsBidirectional[OptBool]):
    is_bidirectional: Annotated[
        OptBool, Field(None, description="Is Bidirectional")
    ] = None


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    Expand,
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[OrganizationRelationIdentifier],
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
            identifier=OrganizationRelationIdentifier(
                type=identifier_type, value=identifier_value
            ),
            data=data,
            expand=expand,
        )


class StatusUpdateParameter(
    Expand,
    BaseStatusUpdateParameter[OrganizationRelationIdentifier],
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
            identifier=OrganizationRelationIdentifier(
                type=identifier_type, value=identifier_value
            ),
            type=type,
            expand=expand,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[OrganizationRelationIdentifier]):
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
            identifier=OrganizationRelationIdentifier(
                type=identifier_type, value=identifier_value
            )
        )
