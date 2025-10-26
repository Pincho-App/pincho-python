"""Basic example of using WirePusher SDK."""

import os
from wirepusher import WirePusher

# Get credentials from environment variables
TOKEN = os.getenv("WIREPUSHER_TOKEN", "wpt_your_token_here")
USER_ID = os.getenv("WIREPUSHER_USER_ID", "your_user_id_here")


def main():
    """Send a basic notification using WirePusher."""
    # Using context manager (recommended)
    with WirePusher(token=TOKEN, user_id=USER_ID) as client:
        # Simple notification
        response = client.send(
            title="Hello from Python!",
            message="This is a test notification from the WirePusher Python SDK.",
        )

        print(f"Status: {response.status}")
        print(f"Message: {response.message}")

        # Notification with all optional parameters
        response = client.send(
            title="Advanced Notification",
            message="This notification has all the bells and whistles!",
            type="demo",
            tags=["python-sdk", "example", "advanced"],
            image_url="https://picsum.photos/400/300",
            action_url="https://github.com/wirepusher/python-sdk",
        )

        print(f"\nAdvanced notification status: {response.status}")


if __name__ == "__main__":
    main()
