from pydantic import Field
from typing import Annotated, Generic
from nexo.schemas.mixins.identity import (
    IdCard as BaseIdCard,
    FullName as BaseFullName,
    BirthPlace as BaseBirthPlace,
    PlaceOfBirth as BasePlaceOfBirth,
)
from nexo.types.string import OptStrT


class IdCard(BaseIdCard[OptStrT], Generic[OptStrT]):
    id_card: Annotated[OptStrT, Field(..., description="Id Card", max_length=16)]


class FullName(BaseFullName[OptStrT], Generic[OptStrT]):
    full_name: Annotated[OptStrT, Field(..., description="Full Name", max_length=200)]


class BirthPlace(BaseBirthPlace[OptStrT], Generic[OptStrT]):
    birth_place: Annotated[
        OptStrT, Field(..., description="Birth Place", max_length=50)
    ]


class PlaceOfBirth(BasePlaceOfBirth[OptStrT], Generic[OptStrT]):
    place_of_birth: Annotated[
        OptStrT, Field(..., description="Place of Birth", max_length=50)
    ]
