from nexo.schemas.resource import Resource, ResourceIdentifier
from nexo.types.string import SeqOfStrs


USER_PROFILE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_profile", name="User Profile", slug="user-profiles"
        )
    ],
    details=None,
)


VALID_EXTENSIONS: SeqOfStrs = (
    ".jpeg",
    ".jpg",
    ".png",
)


VALID_MIME_TYPES: SeqOfStrs = (
    "image/jpeg",
    "image/jpg",
    "image/png",
)
