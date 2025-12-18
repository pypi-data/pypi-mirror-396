from typing import Tuple
from uuid import UUID
from nexo.enums.organization import OrganizationRole


BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, int, OrganizationRole]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
