from nexo.schemas.resource import Resource, ResourceIdentifier

SESSION_RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="session", name="Session", slug="sessions")],
    details=None,
)

VALID_GROUP_DOCUMENT_CONTENT_TYPES: str = "text/csv"
VALID_GROUP_DOCUMENT_EXTENSIONS: str = ".csv"

VALID_INDIVIDUAL_DOCUMENT_CONTENT_TYPES: str = "application/pdf"
VALID_INDIVIDUAL_DOCUMENT_EXTENSIONS: str = ".pdf"
