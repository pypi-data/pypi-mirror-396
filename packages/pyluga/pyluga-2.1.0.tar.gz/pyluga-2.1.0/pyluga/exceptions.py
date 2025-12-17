"""Error classes for Pyluga."""


class PylugaError(Exception):
    """Base error class."""
    pass

class BadRequestError(PylugaError):
    """Raised when a request is passed invalid parameters."""
    pass


class ClientConfigError(PylugaError):
    """Raised when a client configuration error exists."""
    pass


class BelugaApiError(PylugaError):
    """Used to re-raise errors from the Beluga API."""
    pass
