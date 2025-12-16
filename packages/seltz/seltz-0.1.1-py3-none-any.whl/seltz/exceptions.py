"""Custom exceptions for the Seltz SDK."""

import grpc


class SeltzError(Exception):
    """Base exception for all Seltz SDK errors."""

    pass


class SeltzConfigurationError(SeltzError):
    """Raised when there's a configuration issue."""

    pass


class SeltzAuthenticationError(SeltzError):
    """Raised when authentication fails."""

    pass


class SeltzConnectionError(SeltzError):
    """Raised when connection to the API fails."""

    pass


class SeltzAPIError(SeltzError):
    """Raised when the API returns an error."""

    def __init__(
        self,
        message: str,
        grpc_code: grpc.StatusCode | None = None,
        grpc_details: str | None = None,
    ):
        super().__init__(message)
        self.grpc_code = grpc_code
        self.grpc_details = grpc_details


class SeltzTimeoutError(SeltzError):
    """Raised when a request times out."""

    pass


class SeltzRateLimitError(SeltzError):
    """Raised when rate limit is exceeded."""

    pass
