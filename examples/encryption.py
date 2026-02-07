"""Example demonstrating encrypted notifications with Pincho library.

This example shows how to send encrypted notifications where sensitive content
is encrypted. The encrypted fields are: title, message, imageURL, actionURL.
Type and tags remain unencrypted for filtering and routing purposes.

Requirements:
    - Pincho app installed with configured notification type
    - Encryption password set for the notification type in app settings
"""

import os

from pincho import Pincho


def main():
    """Send encrypted notification examples."""

    # Get credentials from environment variables (recommended)
    token = os.getenv("PINCHO_TOKEN")
    encryption_password = os.getenv("PINCHO_ENCRYPTION_PASSWORD")

    if not token:
        print("Error: PINCHO_TOKEN environment variable not set")
        print("Set it with: export PINCHO_TOKEN='abc12345'")
        return

    if not encryption_password:
        print("Error: PINCHO_ENCRYPTION_PASSWORD environment variable not set")
        print("Set it with: export PINCHO_ENCRYPTION_PASSWORD='your_password'")
        return

    # Example 1: Basic encrypted notification
    print("Example 1: Sending encrypted notification...")
    with Pincho(token=token) as client:
        response = client.send(
            title="Secure Alert",  # Encrypted
            message="Your credit card was charged $49.99",  # Encrypted
            type="secure",  # NOT encrypted (needed for password lookup)
            encryption_password=encryption_password,  # Must match app configuration
        )
        print(f"  Status: {response.status}")
        print(f"  Message: {response.message}\n")

    # Example 2: Encrypted notification with all optional parameters
    print("Example 2: Encrypted notification with tags and metadata...")
    with Pincho(token=token) as client:
        response = client.send(
            title="Security Alert",  # Encrypted
            message="Unauthorized login attempt detected from IP 192.168.1.100",  # Encrypted
            type="security",  # NOT encrypted (for filtering)
            tags=["critical", "security", "login"],  # NOT encrypted (for filtering)
            encryption_password=encryption_password,
        )
        print(f"  Status: {response.status}\n")

    # Example 3: Encrypted notification with image and action URL
    print("Example 3: Encrypted notification with URLs...")
    with Pincho(token=token) as client:
        response = client.send(
            title="Payment Alert",  # Encrypted
            message="Your subscription has been renewed for $9.99",  # Encrypted
            type="billing",  # NOT encrypted
            tags=["payment", "subscription"],  # NOT encrypted
            encryption_password=encryption_password,
            image_url="https://example.com/payment-icon.png",  # Encrypted
            action_url="https://example.com/billing/history",  # Encrypted
        )
        print(f"  Status: {response.status}\n")

    # Example 4: Error handling with encryption
    print("Example 4: Error handling...")
    try:
        with Pincho(token=token) as client:
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

    print("All examples completed!")
    print("\nKey points:")
    print("  - Encrypted fields: title, message, imageURL, actionURL")
    print("  - NOT encrypted: type, tags (needed for filtering/routing)")
    print("  - Encryption password must match type configuration in app")
    print("  - Each encrypted notification gets a unique random IV")
    print("  - Unencrypted messages work normally (backward compatible)")


if __name__ == "__main__":
    main()
