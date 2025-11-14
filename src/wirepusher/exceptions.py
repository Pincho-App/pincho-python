"""Custom exceptions for WirePusher library."""


class WirePusherError(Exception):
    """Base exception for WirePusher library.

    All other exceptions in this library inherit from this class.

    Attributes:
        is_retryable: Whether this error indicates a transient issue that may succeed on retry
    """

    is_retryable: bool = False


class AuthenticationError(WirePusherError):
    """Raised when authentication fails.

    This typically occurs when:
    - The API token is invalid or expired
    - The token doesn't have permission
    - The account is disabled

    This error is NOT retryable as credentials won't change between attempts.
    """

    is_retryable = False


class ValidationError(WirePusherError):
    """Raised when request validation fails.

    This typically occurs when:
    - Required parameters are missing
    - Parameters have invalid values
    - The request format is incorrect

    This error is NOT retryable as the same invalid request will fail again.
    """

    is_retryable = False


class RateLimitError(WirePusherError):
    """Raised when rate limit is exceeded (HTTP 429).

    This error IS retryable with exponential backoff.
    The client will automatically retry with longer delays.
    """

    is_retryable = True


class ServerError(WirePusherError):
    """Raised when server returns 5xx error.

    This typically indicates temporary server issues.
    This error IS retryable with exponential backoff.
    """

    is_retryable = True


class NetworkError(WirePusherError):
    """Raised when network communication fails.

    This typically occurs when:
    - Network connection is unavailable
    - DNS resolution fails
    - Connection timeouts

    This error IS retryable with exponential backoff.
    """

    is_retryable = True
