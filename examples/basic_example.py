"""Basic example of using Pincho library."""

import os

from pincho import Pincho

# Get token from environment variable
TOKEN = os.getenv("PINCHO_TOKEN", "abc12345")


def main():
    """Send a basic notification using Pincho."""
    # Using context manager (recommended)
    with Pincho(token=TOKEN) as client:
        # Simple notification
        response = client.send(
            title="Hello from Python!",
            message="This is a test notification from the Pincho Python library.",
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
            action_url="https://github.com/pincho/python-sdk",
        )

        print(f"\nAdvanced notification status: {response.status}")


if __name__ == "__main__":
    main()
