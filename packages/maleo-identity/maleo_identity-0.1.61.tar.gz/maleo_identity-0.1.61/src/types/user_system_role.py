from typing import Tuple
from uuid import UUID
from nexo.enums.system import SystemRole


BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, SystemRole]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
