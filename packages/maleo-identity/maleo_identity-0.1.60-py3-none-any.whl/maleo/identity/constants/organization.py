from nexo.schemas.resource import Resource, ResourceIdentifier


ORGANIZATION_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization", name="Organization", slug="organizations"
        )
    ],
    details=None,
)
