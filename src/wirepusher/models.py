"""Data models for WirePusher SDK."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class NotificationRequest:
    """Notification request model for v1 API.

    Args:
        title: Notification title (max 250 characters)
        message: Notification message body (max 10,000 characters)
        id: User ID (mutually exclusive with token)
            @deprecated Legacy authentication. Use token parameter instead.
        token: Team token (mutually exclusive with id)
        type: Optional notification type for filtering/organization (max 50 characters)
        tags: Optional list of tags (max 10 tags, max 50 characters each)
        imageURL: Optional image URL to display (max 2,000 characters)
        actionURL: Optional URL to open when tapped (max 2,000 characters)
        iv: Optional initialization vector for encrypted messages (hex string, 32 chars)
    """

    title: str
    message: str
    id: Optional[str] = None  # @deprecated Legacy authentication. Use token parameter instead.
    token: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[List[str]] = None
    imageURL: Optional[str] = None
    actionURL: Optional[str] = None
    iv: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class NotificationResponse:
    """Notification response model from WirePusher API.

    Args:
        status: Response status (typically "success" or "error")
        message: Human-readable response message
    """

    status: str
    message: str
