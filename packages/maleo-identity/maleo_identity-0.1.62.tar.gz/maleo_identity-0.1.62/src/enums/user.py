from enum import StrEnum
from nexo.types.string import ListOfStrs


class Granularity(StrEnum):
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    USERNAME = "username"
    EMAIL = "email"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]

    @property
    def column(self) -> str:
        return self.value


class ExpandableField(StrEnum):
    USER_TYPE = "user_type"
    BLOOD_TYPE = "blood_type"
    GENDER = "gender"

    @classmethod
    def choices(cls) -> ListOfStrs:
        return [e.value for e in cls]


OptExpandableField = ExpandableField | None
ListOfExpandableFields = list[ExpandableField]
OptListOfExpandableFields = ListOfExpandableFields | None
