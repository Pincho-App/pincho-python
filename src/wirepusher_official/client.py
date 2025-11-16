"""Synchronous WirePusher client."""

import asyncio
import logging
from typing import Any, Coroutine, List, Optional, TypeVar

from wirepusher_official.async_client import AsyncWirePusher
from wirepusher_official.models import NotifAIResponse, NotificationResponse

T = TypeVar("T")

logger = logging.getLogger("wirepusher_official")


class WirePusher:
    """Synchronous WirePusher client for v1 API.

    This is a synchronous wrapper around AsyncWirePusher, providing a blocking
    API for environments that don't use async/await.

    Features:
        - Automatic retry logic with exponential backoff
        - Tag normalization and validation
        - Message encryption support
        - Comprehensive error handling
        - Debug logging support

    Example:
        >>> # Basic usage
        >>> client = WirePusher(token='abc12345')
        >>> client.send('Team Alert', 'Server maintenance scheduled')
        >>> client.close()

        >>> # Context manager (recommended)
        >>> with WirePusher(token='abc12345') as client:
        ...     client.send('Personal Alert', 'Your task is due soon')
    """

    def __init__(
        self,
        token: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        base_url: Optional[str] = None,
    ):
        """Initialize WirePusher client.

        Args:
            token: WirePusher API token (required)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retry attempts (default: 3, set to 0 to disable)
            base_url: Optional custom base URL (mainly for testing)

        Raises:
            ValueError: If token is not provided

        Examples:
            >>> # Basic usage
            >>> client = WirePusher(token='abc12345')

            >>> # With custom settings
            >>> client = WirePusher(
            ...     token='abc12345',
            ...     timeout=60.0,
            ...     max_retries=5
            ... )
        """
        self._async_client = AsyncWirePusher(
            token=token,
            timeout=timeout,
            max_retries=max_retries,
            base_url=base_url,
        )
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def __enter__(self) -> "WirePusher":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client and release resources.

        Note: In the sync wrapper, closing is best-effort since each request
        uses a new event loop via asyncio.run(). The connections may already
        be cleaned up.
        """
        try:
            self._run_async(self._async_client.close())
        except RuntimeError:
            # Event loop closed error is expected when using asyncio.run()
            # The connections are cleaned up when the loop closes
            pass

    def send(
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
        """Send a notification via WirePusher v1 API.

        Args:
            title: Notification title
            message: Notification message body
            type: Optional notification type for filtering/organization
            tags: Optional list of tags (will be normalized: lowercased, trimmed, deduplicated)
            image_url: Optional image URL to display with notification
            action_url: Optional URL to open when notification is tapped
            encryption_password: Optional password for AES-128-CBC encryption
                (must match type configuration in app)

        Returns:
            NotificationResponse with status and message

        Raises:
            AuthenticationError: Invalid token
            ValidationError: Invalid parameters (missing required fields, etc.)
            RateLimitError: Rate limit exceeded (429)
            ServerError: Server error (5xx)
            NetworkError: Network communication failure
            WirePusherError: Other API errors

        Example:
            >>> client = WirePusher(token='abc12345')
            >>> response = client.send(
            ...     'Deploy Complete',
            ...     'v1.2.3 deployed to production',
            ...     type='deployment',
            ...     tags=['production', 'release']
            ... )
            >>> print(response.status)  # 'success'

        Example with encryption:
            >>> with WirePusher(token='abc12345') as client:
            ...     response = client.send(
            ...         'Secure Message',
            ...         'Sensitive data here',
            ...         type='secure',
            ...         encryption_password='your_password'
            ...     )
        """
        return self._run_async(
            self._async_client.send(
                title=title,
                message=message,
                type=type,
                tags=tags,
                image_url=image_url,
                action_url=action_url,
                encryption_password=encryption_password,
            )
        )

    def notifai(
        self,
        text: str,
        *,
        type: Optional[str] = None,
    ) -> NotifAIResponse:
        """Generate and send AI-powered notification from free-form text.

        Uses Gemini AI to convert natural language into a structured notification
        with auto-generated title, message, tags, and action URL.

        Args:
            text: Free-form text to convert into notification
            type: Optional notification type (overrides AI-generated type)

        Returns:
            NotifAIResponse with status, message, and generated notification details

        Raises:
            AuthenticationError: Invalid token
            ValidationError: Invalid parameters
            RateLimitError: Rate limit exceeded (429)
            ServerError: Server error (5xx)
            NetworkError: Network communication failure
            WirePusherError: Other API errors

        Example:
            >>> with WirePusher(token='abc12345') as client:
            ...     response = client.notifai(
            ...         'deployment finished successfully, v2.1.3 is live on prod'
            ...     )
            ...     print(response.status)  # 'success'
            ...     print(response.notification)  # AI-generated structured notification
        """
        return self._run_async(
            self._async_client.notifai(
                text=text,
                type=type,
            )
        )

    def _run_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run an async coroutine synchronously.

        This method handles running async code in sync context, properly managing
        the event loop lifecycle.

        Args:
            coro: Coroutine to run

        Returns:
            Result from the coroutine
        """
        # Try to get the running event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # We're in an async context - create a new loop to avoid nesting
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                result: T = future.result()
                return result
        else:
            # We're in a sync context - use asyncio.run()
            result_value: T = asyncio.run(coro)
            return result_value
