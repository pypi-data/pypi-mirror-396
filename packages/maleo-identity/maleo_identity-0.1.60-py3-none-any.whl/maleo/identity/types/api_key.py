from typing import Tuple
from uuid import UUID
from nexo.types.integer import OptInt


BasicIdentifierType = int | str | UUID
CompositeIdentifierType = Tuple[int, OptInt]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
