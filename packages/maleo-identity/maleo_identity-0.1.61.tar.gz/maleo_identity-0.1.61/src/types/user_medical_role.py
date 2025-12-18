from typing import Tuple
from uuid import UUID
from nexo.enums.medical import MedicalRole


BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, int, MedicalRole]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
