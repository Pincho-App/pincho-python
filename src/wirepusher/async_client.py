"""Asynchronous WirePusher client."""

from typing import List, Optional

import httpx

from wirepusher.crypto import encrypt_message, generate_iv
from wirepusher.exceptions import AuthenticationError, ValidationError, WirePusherError
from wirepusher.models import NotificationRequest, NotificationResponse


class AsyncWirePusher:
    """Asynchronous WirePusher client for v1 API.

    This client supports both team tokens (for team-wide notifications) and user IDs
    (for personal notifications). Token and user_id are mutually exclusive.

    Example:
        >>> import asyncio
        >>> async def main():
        ...     # Personal notifications
        ...     async with AsyncWirePusher(user_id='user_abc123') as client:
        ...         await client.send('Build Complete', 'Deployed successfully')
        >>> asyncio.run(main())
    """

    BASE_URL = "https://wirepusher.com"

    def __init__(
        self,
        token: Optional[str] = None,
        user_id: Optional[str] = None,
        timeout: float = 30.0,
        base_url: Optional[str] = None,
    ):
        """Initialize async WirePusher client.

        Args:
            token: WirePusher team token (mutually exclusive with user_id)
            user_id: WirePusher user ID (mutually exclusive with token)
            timeout: Request timeout in seconds (default: 30.0)
            base_url: Optional custom base URL (mainly for testing)

        Raises:
            ValueError: If both token and user_id are provided, or if neither is provided

        Examples:
            >>> # Team notifications
            >>> client = AsyncWirePusher(token='wpt_abc123...')

            >>> # Personal notifications
            >>> client = AsyncWirePusher(user_id='user_abc123')
        """
        # Validate mutual exclusivity
        if token and user_id:
            raise ValueError(
                "Cannot specify both 'token' and 'user_id' - they are mutually exclusive. "
                "Use 'token' for team notifications or 'user_id' for personal notifications."
            )
        if not token and not user_id:
            raise ValueError(
                "Must specify either 'token' or 'user_id'. "
                "Use 'token' for team notifications or 'user_id' for personal notifications."
            )

        self.token = token
        self.user_id = user_id
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self._client = httpx.AsyncClient(timeout=timeout)

    async def __aenter__(self) -> "AsyncWirePusher":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()

    async def send(
        self,
        title: str,
        message: str,
        *,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None,
        encryption_password: Optional[str] = None,
    ) -> NotificationResponse:
        """Send a notification via WirePusher v1 API (async).

        Args:
            title: Notification title (max 250 characters)
            message: Notification message body (max 10,000 characters)
            type: Optional notification type for filtering/organization
            tags: Optional list of tags (max 10 tags, max 50 characters each)
            image_url: Optional image URL to display with notification
            action_url: Optional URL to open when notification is tapped
            encryption_password: Optional password for AES-128-CBC encryption
                (must match type configuration in app)

        Returns:
            NotificationResponse with status and message

        Raises:
            AuthenticationError: Invalid token or user ID
            ValidationError: Invalid parameters (missing required fields, etc.)
            WirePusherError: Other API errors (network issues, server errors, etc.)

        Example:
            >>> async with AsyncWirePusher(token='wpt_abc123', user_id='user123') as client:
            ...     response = await client.send(
            ...         'Deploy Complete',
            ...         'v1.2.3 deployed to production',
            ...         type='deployment',
            ...         tags=['production', 'release']
            ...     )
            ...     print(response.status)  # 'success'

        Example with encryption:
            >>> async with AsyncWirePusher(user_id='user123') as client:
            ...     response = await client.send(
            ...         'Secure Message',
            ...         'Sensitive data here',
            ...         type='secure',
            ...         encryption_password='your_password'
            ...     )
        """
        # Handle encryption if password provided
        final_message = message
        iv_hex: Optional[str] = None

        if encryption_password:
            iv_bytes, iv_hex = generate_iv()
            final_message = encrypt_message(message, encryption_password, iv_bytes)

        request = NotificationRequest(
            title=title,
            message=final_message,
            id=self.user_id,
            token=self.token,
            type=type,
            tags=tags,
            imageURL=image_url,
            actionURL=action_url,
            iv=iv_hex,
        )

        try:
            response = await self._client.post(
                f"{self.base_url}/send",
                json=request.to_dict(),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            data = response.json()
            return NotificationResponse(
                status=data.get("status", "unknown"),
                message=data.get("message", ""),
            )

        except httpx.HTTPStatusError as e:
            # Handle specific HTTP error codes
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid token or user ID. Please check your credentials."
                ) from e
            elif e.response.status_code == 400:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("message", e.response.text)
                except Exception:
                    error_message = e.response.text
                raise ValidationError(f"Invalid parameters: {error_message}") from e
            elif e.response.status_code == 403:
                raise AuthenticationError(
                    "Forbidden: Your account may be disabled or you don't have permission."
                ) from e
            elif e.response.status_code == 404:
                raise ValidationError("User not found. Please check your user ID.") from e
            else:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("message", e.response.text)
                except Exception:
                    error_message = e.response.text
                raise WirePusherError(
                    f"API error ({e.response.status_code}): {error_message}"
                ) from e

        except httpx.RequestError as e:
            raise WirePusherError(f"Network error: {str(e)}") from e

        except Exception as e:
            raise WirePusherError(f"Unexpected error: {str(e)}") from e
