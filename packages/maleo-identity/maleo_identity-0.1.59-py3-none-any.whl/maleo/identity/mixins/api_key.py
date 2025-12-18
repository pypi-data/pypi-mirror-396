from pydantic import BaseModel, Field
from typing import Annotated, Literal, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier
from nexo.types.any import ManyAny
from nexo.types.string import ManyStrs
from ..enums.api_key import IdentifierType
from ..types.api_key import CompositeIdentifierType, IdentifierValueType


class APIKey(BaseModel):
    api_key: Annotated[str, Field(..., description="API Key", max_length=255)]


class APIKeyIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def columns_and_values(self) -> tuple[ManyStrs, ManyAny]:
        values = self.value if isinstance(self.value, tuple) else (self.value,)
        return self.type.columns, values


class IdAPIKeyIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDAPIKeyIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class APIKeyAPIKeyIdentifier(Identifier[Literal[IdentifierType.API_KEY], str]):
    type: Annotated[
        Literal[IdentifierType.API_KEY],
        Field(IdentifierType.API_KEY, description="Identifier's type"),
    ] = IdentifierType.API_KEY


class CompositeAPIKeyIdentifier(
    Identifier[Literal[IdentifierType.COMPOSITE], CompositeIdentifierType]
):
    type: Annotated[
        Literal[IdentifierType.COMPOSITE],
        Field(IdentifierType.COMPOSITE, description="Identifier's type"),
    ] = IdentifierType.COMPOSITE
    value: Annotated[
        CompositeIdentifierType, Field(..., description="Identifier's value")
    ]


AnyAPIKeyIdentifier = (
    APIKeyIdentifier
    | IdAPIKeyIdentifier
    | UUIDAPIKeyIdentifier
    | APIKeyAPIKeyIdentifier
    | CompositeAPIKeyIdentifier
)


def is_id_identifier(
    identifier: AnyAPIKeyIdentifier,
) -> TypeGuard[IdAPIKeyIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_api_key_identifier(
    identifier: AnyAPIKeyIdentifier,
) -> TypeGuard[APIKeyAPIKeyIdentifier]:
    return identifier.type is IdentifierType.API_KEY and isinstance(
        identifier.value, str
    )


def is_uuid_identifier(
    identifier: AnyAPIKeyIdentifier,
) -> TypeGuard[UUIDAPIKeyIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_composite_identifier(
    identifier: AnyAPIKeyIdentifier,
) -> TypeGuard[CompositeAPIKeyIdentifier]:
    return identifier.type is IdentifierType.COMPOSITE and isinstance(
        identifier.value, tuple
    )
