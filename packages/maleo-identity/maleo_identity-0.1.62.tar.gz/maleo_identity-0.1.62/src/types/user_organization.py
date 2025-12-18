from typing import Tuple
from uuid import UUID


BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, int]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
