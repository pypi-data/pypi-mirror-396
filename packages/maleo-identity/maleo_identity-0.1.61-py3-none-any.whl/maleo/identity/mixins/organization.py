from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier, Key as BaseKey, Name as BaseName
from nexo.types.string import OptStrT
from nexo.types.uuid import OptUUIDT
from ..enums.organization import IdentifierType, OptListOfExpandableFields
from ..types.organization import IdentifierValueType


class Key(BaseKey, Generic[OptStrT]):
    key: Annotated[OptStrT, Field(..., description="Key", max_length=255)]


class Name(BaseName, Generic[OptStrT]):
    name: Annotated[OptStrT, Field(..., description="Name", max_length=255)]


class Secret(BaseModel, Generic[OptUUIDT]):
    secret: Annotated[OptUUIDT, Field(..., description="Secret")]


class Expand(BaseModel):
    expand: Annotated[
        OptListOfExpandableFields, Field(None, description="Expanded field(s)")
    ] = None


class OrganizationIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdOrganizationIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDOrganizationIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class KeyOrganizationIdentifier(Identifier[Literal[IdentifierType.KEY], str]):
    type: Annotated[
        Literal[IdentifierType.KEY],
        Field(IdentifierType.KEY, description="Identifier's type"),
    ] = IdentifierType.KEY
    value: Annotated[str, Field(..., description="Identifier's value", max_length=255)]


AnyOrganizationIdentifier = (
    OrganizationIdentifier
    | IdOrganizationIdentifier
    | UUIDOrganizationIdentifier
    | KeyOrganizationIdentifier
)


def is_id_identifier(
    identifier: AnyOrganizationIdentifier,
) -> TypeGuard[IdOrganizationIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyOrganizationIdentifier,
) -> TypeGuard[UUIDOrganizationIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_key_identifier(
    identifier: AnyOrganizationIdentifier,
) -> TypeGuard[KeyOrganizationIdentifier]:
    return identifier.type is IdentifierType.KEY and isinstance(identifier.value, str)
