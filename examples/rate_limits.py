"""Rate limit monitoring example for Pincho.

This example demonstrates how to monitor and work with API rate limits
using the last_rate_limit property available on both sync and async clients.

Features demonstrated:
    - Accessing rate limit information after requests
    - Proactive rate limit checking
    - Rate limit aware batch sending
    - Async rate limit monitoring
"""

import asyncio
import os
from datetime import datetime

from pincho import AsyncPincho, Pincho

# Get token from environment variable
TOKEN = os.getenv("PINCHO_TOKEN", "abc12345")


def basic_rate_limit_check():
    """Basic rate limit checking after a request."""
    print("Example 1: Basic Rate Limit Check")
    print("-" * 40)

    with Pincho(token=TOKEN) as client:
        response = client.send(
            title="Rate Limit Test",
            message="Checking rate limit information",
            type="test",
        )

        print(f"Response: {response.status}")

        # Check rate limit info
        if client.last_rate_limit:
            info = client.last_rate_limit
            print("Rate Limit Status:")
            print(f"  Remaining: {info.remaining}/{info.limit}")
            print(f"  Resets at: {info.reset}")

            # Calculate time until reset
            time_until_reset = info.reset - datetime.now()
            print(f"  Time until reset: {time_until_reset.total_seconds():.0f} seconds")
        else:
            print("  No rate limit headers in response")

    print()


def proactive_rate_limit_checking():
    """Proactively check rate limits before sending."""
    print("Example 2: Proactive Rate Limit Checking")
    print("-" * 40)

    with Pincho(token=TOKEN) as client:
        # First request to get rate limit info
        client.send("Initial", "Getting rate limit info")

        if client.last_rate_limit:
            remaining = client.last_rate_limit.remaining
            limit = client.last_rate_limit.limit

            print(f"Current status: {remaining}/{limit} requests remaining")

            # Check thresholds
            usage_percent = ((limit - remaining) / limit) * 100

            if remaining < 10:
                print("  WARNING: Very low on remaining requests!")
            elif remaining < 50:
                print("  CAUTION: Approaching rate limit threshold")
            else:
                print("  OK: Plenty of requests remaining")

            print(f"  Usage: {usage_percent:.1f}% of limit used")

    print()


def rate_limit_aware_batch():
    """Send multiple notifications with rate limit awareness."""
    print("Example 3: Rate Limit Aware Batch Sending")
    print("-" * 40)

    messages = [
        ("Alert 1", "First message"),
        ("Alert 2", "Second message"),
        ("Alert 3", "Third message"),
        ("Alert 4", "Fourth message"),
        ("Alert 5", "Fifth message"),
    ]

    with Pincho(token=TOKEN) as client:
        for i, (title, message) in enumerate(messages, 1):
            print(f"Sending message {i}/{len(messages)}...")
            client.send(title, message, type="batch")

            if client.last_rate_limit:
                remaining = client.last_rate_limit.remaining
                print(f"  Remaining: {remaining}")

                # Stop if running low
                if remaining < 3:
                    print(f"  STOPPING: Only {remaining} requests remaining")
                    print(f"  Would resume at: {client.last_rate_limit.reset}")
                    break
            else:
                print("  No rate limit info available")

    print()


def multiple_requests_tracking():
    """Track rate limit changes across multiple requests."""
    print("Example 4: Track Rate Limits Across Requests")
    print("-" * 40)

    with Pincho(token=TOKEN) as client:
        # Send 3 requests and track changes
        for i in range(3):
            client.send(f"Test {i+1}", f"Message number {i+1}")

            if client.last_rate_limit:
                print(f"After request {i+1}: {client.last_rate_limit.remaining} remaining")

    print()


async def async_rate_limit_monitoring():
    """Monitor rate limits with async client."""
    print("Example 5: Async Rate Limit Monitoring")
    print("-" * 40)

    async with AsyncPincho(token=TOKEN) as client:
        # Send concurrent requests
        tasks = [client.send(f"Async {i}", f"Message {i}") for i in range(3)]

        responses = await asyncio.gather(*tasks)
        print(f"Sent {len(responses)} concurrent notifications")

        # Check final rate limit status
        if client.last_rate_limit:
            info = client.last_rate_limit
            print("Final rate limit status:")
            print(f"  Remaining: {info.remaining}/{info.limit}")
            print(f"  Resets at: {info.reset}")

    print()


def rate_limit_safe_sender():
    """A helper class for rate-limit-safe sending."""
    print("Example 6: Rate Limit Safe Sender Pattern")
    print("-" * 40)

    class SafeSender:
        """Send notifications with rate limit protection."""

        def __init__(self, min_remaining: int = 5):
            self.min_remaining = min_remaining
            self.client = Pincho(token=TOKEN)

        def __enter__(self):
            self.client.__enter__()
            return self

        def __exit__(self, *args):
            self.client.__exit__(*args)

        def can_send(self) -> bool:
            """Check if safe to send based on rate limits."""
            if self.client.last_rate_limit is None:
                return True  # No info yet, try sending
            return self.client.last_rate_limit.remaining > self.min_remaining

        def send(self, title: str, message: str, **kwargs):
            """Send with rate limit check."""
            if not self.can_send():
                reset_time = self.client.last_rate_limit.reset
                raise RuntimeError(f"Rate limit too low, resets at {reset_time}")

            return self.client.send(title, message, **kwargs)

        def remaining(self) -> int:
            """Get remaining requests."""
            if self.client.last_rate_limit:
                return self.client.last_rate_limit.remaining
            return -1  # Unknown

    # Use the safe sender
    with SafeSender(min_remaining=2) as sender:
        sender.send("Safe Send 1", "First safe message")
        print(f"Sent message, {sender.remaining()} requests remaining")

        sender.send("Safe Send 2", "Second safe message")
        print(f"Sent message, {sender.remaining()} requests remaining")

    print()


def main():
    """Run all rate limit examples."""
    print("=" * 50)
    print("Pincho Rate Limit Monitoring Examples")
    print("=" * 50)
    print()

    # Run sync examples
    basic_rate_limit_check()
    proactive_rate_limit_checking()
    multiple_requests_tracking()
    rate_limit_aware_batch()
    rate_limit_safe_sender()

    # Run async example
    asyncio.run(async_rate_limit_monitoring())

    print("=" * 50)
    print("All examples completed!")
    print()
    print("Key takeaways:")
    print("  - Access rate limits via client.last_rate_limit")
    print("  - Check remaining requests before high-volume operations")
    print("  - The reset time tells you when limits refresh")
    print("  - Both sync and async clients support rate limit tracking")
    print("  - Rate limit info is updated after every request")


if __name__ == "__main__":
    main()
