"""Database exceptions."""

from starlette import status


class DatabaseError(Exception):
    """Generic database error."""

    pass


class DomainNotExistsError(DatabaseError):
    """Domain does not exist."""

    def __init__(self) -> None:
        """Set attributes."""
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "No security.txt policy exists for this domain."
