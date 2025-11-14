"""Async example of using WirePusher library."""

import asyncio
import os
from wirepusher import AsyncWirePusher

# Get token from environment variable
TOKEN = os.getenv("WIREPUSHER_TOKEN", "abc12345")


async def send_single_notification():
    """Send a single notification asynchronously."""
    async with AsyncWirePusher(token=TOKEN) as client:
        response = await client.send(
            title="Async Notification",
            message="Sent using async/await!",
            type="async-demo",
        )
        print(f"Single notification: {response.status}")


async def send_multiple_concurrent():
    """Send multiple notifications concurrently (demonstrates async benefit)."""
    async with AsyncWirePusher(token=TOKEN) as client:
        # Create multiple notification tasks
        tasks = [
            client.send(f"Notification {i}", f"This is message number {i}")
            for i in range(1, 4)
        ]

        # Execute all tasks concurrently
        responses = await asyncio.gather(*tasks)

        print(f"\nSent {len(responses)} notifications concurrently!")
        for i, response in enumerate(responses, 1):
            print(f"  Notification {i}: {response.status}")


async def main():
    """Run all async examples."""
    print("=== Single Notification ===")
    await send_single_notification()

    print("\n=== Concurrent Notifications ===")
    await send_multiple_concurrent()


if __name__ == "__main__":
    asyncio.run(main())
