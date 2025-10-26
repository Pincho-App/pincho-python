"""Synchronous WirePusher client."""

from typing import List, Optional

import httpx

from wirepusher.exceptions import AuthenticationError, ValidationError, WirePusherError
from wirepusher.models import NotificationRequest, NotificationResponse


class WirePusher:
    """Synchronous WirePusher client for v1 API.

    This client uses WirePusher API tokens for authentication, making it ideal for
    automation, scripts, data pipelines, and server-side applications.

    Example:
        >>> client = WirePusher(token='wpt_abc123', user_id='user123')
        >>> client.send('Build Complete', 'v1.2.3 deployed successfully')

        >>> # Using context manager (recommended)
        >>> with WirePusher(token='wpt_abc123', user_id='user123') as client:
        ...     client.send('Alert', 'Server is down')
    """

    BASE_URL = "https://wirepusher-gateway-1xatwfdc.uc.gateway.dev"

    def __init__(
        self,
        token: str,
        user_id: str,
        timeout: float = 30.0,
        base_url: Optional[str] = None,
    ):
        """Initialize WirePusher client.

        Args:
            token: WirePusher API token (get from app settings)
            user_id: WirePusher user ID
            timeout: Request timeout in seconds (default: 30.0)
            base_url: Optional custom base URL (mainly for testing)
        """
        self.token = token
        self.user_id = user_id
        self.timeout = timeout
        self.base_url = base_url or self.BASE_URL
        self._client = httpx.Client(timeout=timeout)

    def __enter__(self) -> "WirePusher":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    def send(
        self,
        title: str,
        message: str,
        *,
        type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        image_url: Optional[str] = None,
        action_url: Optional[str] = None,
    ) -> NotificationResponse:
        """Send a notification via WirePusher v1 API.

        Args:
            title: Notification title (max 250 characters)
            message: Notification message body (max 10,000 characters)
            type: Optional notification type for filtering/organization
            tags: Optional list of tags (max 10 tags, max 50 characters each)
            image_url: Optional image URL to display with notification
            action_url: Optional URL to open when notification is tapped

        Returns:
            NotificationResponse with status and message

        Raises:
            AuthenticationError: Invalid token or user ID
            ValidationError: Invalid parameters (missing required fields, etc.)
            WirePusherError: Other API errors (network issues, server errors, etc.)

        Example:
            >>> client = WirePusher(token='wpt_abc123', user_id='user123')
            >>> response = client.send(
            ...     'Deploy Complete',
            ...     'v1.2.3 deployed to production',
            ...     type='deployment',
            ...     tags=['production', 'release']
            ... )
            >>> print(response.status)  # 'success'
        """
        request = NotificationRequest(
            title=title,
            message=message,
            id=self.user_id,
            token=self.token,
            type=type,
            tags=tags,
            imageURL=image_url,
            actionURL=action_url,
        )

        try:
            response = self._client.post(
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
