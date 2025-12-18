from enum import StrEnum
from nexo.types.string import ListOfStrs, ManyStrs


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    API_KEY = "api_key"
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
        elif self is IdentifierType.API_KEY:
            return ("api_key",)
        elif self is IdentifierType.COMPOSITE:
            return ("user_id", "organization_id")
        raise ValueError(f"Unknown column(s) for identifier type: {self}")
