from enum import StrEnum
from nexo.types.string import ListOfStrs, ManyStrs


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    COMPOSITE = "composite"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def columns(self) -> ManyStrs:
        if self is IdentifierType.ID:
            return ("id",)
        elif self is IdentifierType.UUID:
            return ("uuid",)
        elif self is IdentifierType.COMPOSITE:
            return ("user_id", "organization_id", "organization_role")
        raise ValueError(f"Unknown column(s) for identifier type: {self}")


class ExpandableField(StrEnum):
    ORGANIZATION_ROLE = "organization_role"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


OptExpandableField = ExpandableField | None
ListOfExpandableFields = list[ExpandableField]
OptListOfExpandableFields = ListOfExpandableFields | None
