from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier
from nexo.types.string import OptStrT
from ..enums.user_profile import IdentifierType, OptListOfExpandableFields
from ..types.user_profile import IdentifierValueType


class LeadingTitle(BaseModel, Generic[OptStrT]):
    leading_title: Annotated[
        OptStrT, Field(..., description="User's Leading Title", max_length=25)
    ]


class FirstName(BaseModel, Generic[OptStrT]):
    first_name: Annotated[
        OptStrT, Field(..., description="User's First Name", max_length=50)
    ]


class MiddleName(BaseModel, Generic[OptStrT]):
    middle_name: Annotated[
        OptStrT, Field(..., description="User's Middle Name", max_length=50)
    ]


class LastName(BaseModel, Generic[OptStrT]):
    last_name: Annotated[
        OptStrT, Field(..., description="User's Last Name", max_length=50)
    ]


class EndingTitle(BaseModel, Generic[OptStrT]):
    ending_title: Annotated[
        OptStrT, Field(..., description="User's Ending Title", max_length=25)
    ]


class Avatar(BaseModel):
    content: Annotated[bytes, Field(..., description="Avatar's content")]
    content_type: Annotated[str, Field(..., description="Avatar's content type")]
    filename: Annotated[str, Field(..., description="Avatar's filename")]


OptAvatar = Avatar | None


class AvatarMixin(BaseModel):
    avatar: Annotated[OptAvatar, Field(None, description="Avatar")]


class AvatarName(BaseModel, Generic[OptStrT]):
    avatar_name: Annotated[OptStrT, Field(..., description="User's Avatar Name")]


class AvatarUrl(BaseModel, Generic[OptStrT]):
    avatar_url: Annotated[OptStrT, Field(..., description="User's Avatar URL")]


class Expand(BaseModel):
    expand: Annotated[
        OptListOfExpandableFields, Field(None, description="Expanded field(s)")
    ] = None


class UserProfileIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdUserProfileIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UserIdUserProfileIdentifier(Identifier[Literal[IdentifierType.USER_ID], int]):
    type: Annotated[
        Literal[IdentifierType.USER_ID],
        Field(IdentifierType.USER_ID, description="Identifier's type"),
    ] = IdentifierType.USER_ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDUserProfileIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class IdCardUserProfileIdentifier(Identifier[Literal[IdentifierType.ID_CARD], str]):
    type: Annotated[
        Literal[IdentifierType.ID_CARD],
        Field(IdentifierType.ID_CARD, description="Identifier's type"),
    ] = IdentifierType.ID_CARD
    value: Annotated[str, Field(..., description="Identifier's value", max_length=16)]


AnyUserProfileIdentifier = (
    UserProfileIdentifier
    | IdUserProfileIdentifier
    | UserIdUserProfileIdentifier
    | UUIDUserProfileIdentifier
    | IdCardUserProfileIdentifier
)


def is_id_identifier(
    identifier: AnyUserProfileIdentifier,
) -> TypeGuard[IdUserProfileIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_user_id_identifier(
    identifier: AnyUserProfileIdentifier,
) -> TypeGuard[UserIdUserProfileIdentifier]:
    return identifier.type is IdentifierType.USER_ID and isinstance(
        identifier.value, int
    )


def is_uuid_identifier(
    identifier: AnyUserProfileIdentifier,
) -> TypeGuard[UUIDUserProfileIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_id_card_identifier(
    identifier: AnyUserProfileIdentifier,
) -> TypeGuard[IdCardUserProfileIdentifier]:
    return identifier.type is IdentifierType.ID_CARD and isinstance(
        identifier.value, str
    )
