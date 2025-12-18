from typing import Tuple
from uuid import UUID
from nexo.enums.organization import OrganizationRelation

BasicIdentifierType = int | UUID
CompositeIdentifierType = Tuple[int, int, OrganizationRelation]
IdentifierValueType = BasicIdentifierType | CompositeIdentifierType
