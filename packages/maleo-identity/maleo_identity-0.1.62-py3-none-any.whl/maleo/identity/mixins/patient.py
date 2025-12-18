from pydantic import BaseModel, Field, model_validator
from typing import Annotated, Generic, Literal, Self, TypeGuard
from uuid import UUID
from nexo.schemas.mixins.identity import Identifier, Passport as BasePassport
from nexo.types.string import OptStr, OptStrT
from ..enums.patient import IdentifierType, OptListOfExpandableFields
from ..types.patient import IdentifierValueType
from .common import IdCard


class Passport(BasePassport, Generic[OptStrT]):
    passport: Annotated[OptStrT, Field(..., description="Passport", max_length=9)]


class PatientIdentity(
    Passport[OptStr],
    IdCard[OptStr],
):
    @model_validator(mode="after")
    def chk_id_card_or_passport(self) -> Self:
        if self.id_card is None and self.passport is None:
            raise ValueError("Either ID Card or Passport must exist")
        return self


class Expand(BaseModel):
    expand: Annotated[
        OptListOfExpandableFields, Field(None, description="Expanded field(s)")
    ] = None


class PatientIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdPatientIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDPatientIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


AnyPatientIdentifier = PatientIdentifier | IdPatientIdentifier | UUIDPatientIdentifier


def is_id_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[IdPatientIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[UUIDPatientIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)
