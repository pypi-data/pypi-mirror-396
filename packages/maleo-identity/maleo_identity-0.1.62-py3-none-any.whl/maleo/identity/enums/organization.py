from enum import StrEnum
from nexo.types.string import ListOfStrs


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def column(self) -> str:
        return self.value


class ExpandableField(StrEnum):
    ORGANIZATION_TYPE = "organization_type"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


OptExpandableField = ExpandableField | None
ListOfExpandableFields = list[ExpandableField]
OptListOfExpandableFields = ListOfExpandableFields | None
