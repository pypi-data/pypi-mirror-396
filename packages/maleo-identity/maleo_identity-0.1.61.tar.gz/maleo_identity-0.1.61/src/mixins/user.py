from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier
from nexo.types.string import OptStrT, OptListOfStrsT
from ..enums.user import IdentifierType, OptListOfExpandableFields
from ..types.user import IdentifierValueType


class Username(BaseModel, Generic[OptStrT]):
    username: Annotated[
        OptStrT, Field(..., description="User's username", max_length=50)
    ]


class Usernames(BaseModel, Generic[OptListOfStrsT]):
    usernames: Annotated[OptListOfStrsT, Field(..., description="User's Usernames")]


class Email(BaseModel, Generic[OptStrT]):
    email: Annotated[OptStrT, Field(..., description="User's email", max_length=255)]


class Emails(BaseModel, Generic[OptListOfStrsT]):
    emails: Annotated[OptListOfStrsT, Field(..., description="User's Emails")]


class Phone(BaseModel, Generic[OptStrT]):
    phone: Annotated[OptStrT, Field(..., description="User's phone", max_length=15)]


class Phones(BaseModel, Generic[OptListOfStrsT]):
    phones: Annotated[OptListOfStrsT, Field(..., description="User's Phones")]


class Password(BaseModel):
    password: Annotated[str, Field(..., description="Password", max_length=255)]


class Expand(BaseModel):
    expand: Annotated[
        OptListOfExpandableFields, Field(None, description="Expanded field(s)")
    ] = None


class UserIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdUserIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDUserIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class UsernameUserIdentifier(Identifier[Literal[IdentifierType.USERNAME], str]):
    type: Annotated[
        Literal[IdentifierType.USERNAME],
        Field(IdentifierType.USERNAME, description="Identifier's type"),
    ] = IdentifierType.USERNAME
    value: Annotated[str, Field(..., description="Identifier's value", max_length=50)]


class EmailUserIdentifier(Identifier[Literal[IdentifierType.EMAIL], str]):
    type: Annotated[
        Literal[IdentifierType.EMAIL],
        Field(IdentifierType.EMAIL, description="Identifier's type"),
    ] = IdentifierType.EMAIL
    value: Annotated[str, Field(..., description="Identifier's value", max_length=255)]


AnyUserIdentifier = (
    UserIdentifier
    | IdUserIdentifier
    | UUIDUserIdentifier
    | UsernameUserIdentifier
    | EmailUserIdentifier
)


def is_id_identifier(
    identifier: AnyUserIdentifier,
) -> TypeGuard[IdUserIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyUserIdentifier,
) -> TypeGuard[UUIDUserIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_username_identifier(
    identifier: AnyUserIdentifier,
) -> TypeGuard[UsernameUserIdentifier]:
    return identifier.type is IdentifierType.USERNAME and isinstance(
        identifier.value, str
    )


def is_email_identifier(
    identifier: AnyUserIdentifier,
) -> TypeGuard[EmailUserIdentifier]:
    return identifier.type is IdentifierType.EMAIL and isinstance(identifier.value, str)
