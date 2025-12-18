from nexo.schemas.resource import Resource, ResourceIdentifier


API_KEY_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="api_key",
            name="API Key",
            slug="api-keys",
        )
    ],
    details=None,
)
