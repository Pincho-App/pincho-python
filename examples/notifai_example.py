"""NotifAI example - AI-powered notification generation.

This example demonstrates how to use the NotifAI endpoint to generate
structured notifications from free-form text using Gemini AI.

The AI automatically generates:
- Title and message
- Relevant tags
- Action URL (when applicable)
- Notification type (or you can override it)
"""

import os
from wirepusher import WirePusher
from wirepusher.exceptions import WirePusherError

# Get token from environment variable
TOKEN = os.getenv("WIREPUSHER_TOKEN", "abc12345")


def main():
    """Demonstrate NotifAI capabilities."""

    # Example 1: Basic NotifAI usage
    print("Example 1: Basic AI-generated notification...")
    with WirePusher(token=TOKEN) as client:
        response = client.notifai(
            'deployment finished successfully, v2.1.3 is live on production'
        )

        print(f"  Status: {response.status}")
        print(f"  Message: {response.message}")
        if response.notification:
            print(f"  AI Generated:")
            print(f"    Title: {response.notification.get('title')}")
            print(f"    Message: {response.notification.get('message')}")
            print(f"    Type: {response.notification.get('type')}")
            print(f"    Tags: {response.notification.get('tags')}\n")

    # Example 2: System monitoring alert
    print("Example 2: System monitoring alert...")
    with WirePusher(token=TOKEN) as client:
        response = client.notifai(
            'cpu at 95% on web-3, memory usage is high, might need to restart'
        )

        if response.notification:
            print(f"  AI Generated:")
            print(f"    Title: {response.notification.get('title')}")
            print(f"    Message: {response.notification.get('message')}")
            print(f"    Tags: {response.notification.get('tags')}\n")

    # Example 3: Override AI-generated type
    print("Example 3: Override AI type...")
    with WirePusher(token=TOKEN) as client:
        response = client.notifai(
            'new user signup, email: user@example.com',
            type='user-activity'  # Override AI type
        )

        if response.notification:
            print(f"  AI Generated (with type override):")
            print(f"    Title: {response.notification.get('title')}")
            print(f"    Message: {response.notification.get('message')}")
            print(f"    Type: {response.notification.get('type')}")
            print(f"    Tags: {response.notification.get('tags')}\n")

    # Example 4: Sales/business event
    print("Example 4: Business event...")
    with WirePusher(token=TOKEN) as client:
        response = client.notifai(
            'new order placed, $249.99, premium plan subscription'
        )

        if response.notification:
            print(f"  AI Generated:")
            print(f"    Title: {response.notification.get('title')}")
            print(f"    Message: {response.notification.get('message')}")
            print(f"    Tags: {response.notification.get('tags')}\n")

    # Example 5: Error handling
    print("Example 5: Error handling...")
    try:
        with WirePusher(token=TOKEN) as client:
            # Empty text should fail validation
            response = client.notifai('')
    except WirePusherError as e:
        print(f"  Expected error: {e}\n")

    print("✓ All NotifAI examples completed!")
    print("\nKey points:")
    print("  - AI generates title, message, tags, and type from free-form text")
    print("  - Useful for quick notifications without manual formatting")
    print("  - Can override AI-generated type if needed")
    print("  - Works with both sync and async clients")


if __name__ == '__main__':
    main()
