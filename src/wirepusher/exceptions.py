"""Custom exceptions for WirePusher SDK."""


class WirePusherError(Exception):
    """Base exception for WirePusher SDK.

    All other exceptions in this SDK inherit from this class.
    """

    pass


class AuthenticationError(WirePusherError):
    """Raised when authentication fails.

    This typically occurs when:
    - The API token is invalid or expired
    - The user ID is incorrect
    - The token doesn't have permission for the user ID
    """

    pass


class ValidationError(WirePusherError):
    """Raised when request validation fails.

    This typically occurs when:
    - Required parameters are missing
    - Parameters have invalid values
    - The request format is incorrect
    """

    pass
