"""Example demonstrating encrypted notifications with WirePusher library.

This example shows how to send encrypted notifications where only the message
content is encrypted. Title, type, tags, and other metadata remain unencrypted
for filtering and display purposes.

Requirements:
    - WirePusher app installed with configured notification type
    - Encryption password set for the notification type in app settings
"""

import os

from wirepusher_official import WirePusher


def main():
    """Send encrypted notification examples."""

    # Get credentials from environment variables (recommended)
    token = os.getenv("WIREPUSHER_TOKEN")
    encryption_password = os.getenv("WIREPUSHER_ENCRYPTION_PASSWORD")

    if not token:
        print("Error: WIREPUSHER_TOKEN environment variable not set")
        print("Set it with: export WIREPUSHER_TOKEN='abc12345'")
        return

    if not encryption_password:
        print("Error: WIREPUSHER_ENCRYPTION_PASSWORD environment variable not set")
        print("Set it with: export WIREPUSHER_ENCRYPTION_PASSWORD='your_password'")
        return

    # Example 1: Basic encrypted notification
    print("Example 1: Sending encrypted notification...")
    with WirePusher(token=token) as client:
        response = client.send(
            title="Secure Alert",  # NOT encrypted (for display)
            message="Your credit card was charged $49.99",  # Encrypted
            type="secure",  # NOT encrypted (needed for password lookup)
            encryption_password=encryption_password,  # Must match app configuration
        )
        print(f"  Status: {response.status}")
        print(f"  Message: {response.message}\n")

    # Example 2: Encrypted notification with all optional parameters
    print("Example 2: Encrypted notification with tags and metadata...")
    with WirePusher(token=token) as client:
        response = client.send(
            title="Security Alert",
            message="Unauthorized login attempt detected from IP 192.168.1.100",
            type="security",
            tags=["critical", "security", "login"],  # NOT encrypted
            encryption_password=encryption_password,
        )
        print(f"  Status: {response.status}\n")

    # Example 3: Encrypted notification with image and action URL
    print("Example 3: Encrypted notification with additional metadata...")
    with WirePusher(token=token) as client:
        response = client.send(
            title="Payment Alert",
            message="Your subscription has been renewed for $9.99",
            type="billing",
            tags=["payment", "subscription"],
            encryption_password=encryption_password,
            image_url="https://example.com/payment-icon.png",
            action_url="https://example.com/billing/history",
        )
        print(f"  Status: {response.status}\n")

    # Example 4: Error handling with encryption
    print("Example 4: Error handling...")
    try:
        with WirePusher(token=token) as client:
            # This will work - encryption is optional
            response = client.send(
                title="Unencrypted Message",
                message="This message is sent in plain text",
                type="info",
                # No encryption_password provided
            )
            print(f"  Unencrypted notification sent: {response.status}")

            # This will also work - encryption with password
            response = client.send(
                title="Encrypted Message",
                message="This message is encrypted",
                type="secure",
                encryption_password=encryption_password,
            )
            print(f"  Encrypted notification sent: {response.status}\n")

    except Exception as e:
        print(f"  Error: {e}\n")

    print("✓ All examples completed!")
    print("\nKey points:")
    print("  - Only the 'message' field is encrypted")
    print("  - Title, type, tags, imageURL, actionURL remain unencrypted")
    print("  - Encryption password must match type configuration in app")
    print("  - Each encrypted message gets a unique random IV")
    print("  - Unencrypted messages work normally (backward compatible)")


if __name__ == "__main__":
    main()
