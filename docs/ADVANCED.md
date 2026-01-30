# Advanced Usage Guide

This document covers advanced configuration options and usage patterns for the Pincho Python library.

## Table of Contents

- [Rate Limit Monitoring](#rate-limit-monitoring)
- [Retry-After Behavior](#retry-after-behavior)
- [Logging Configuration](#logging-configuration)
- [Async vs Sync Clients](#async-vs-sync-clients)
- [Custom Configuration](#custom-configuration)

## Rate Limit Monitoring

The library automatically tracks rate limit information from API responses. After each request, you can access the `last_rate_limit` property to monitor your API usage.

### Basic Rate Limit Checking

```python
from pincho import Pincho

with Pincho() as client:
    response = client.send('Alert', 'Server restarted')

    # Check rate limit status
    if client.last_rate_limit:
        info = client.last_rate_limit
        print(f"Requests remaining: {info.remaining}/{info.limit}")
        print(f"Window resets at: {info.reset}")

        # Proactive rate limit checking
        if info.remaining < 10:
            print("Warning: Approaching rate limit!")
```

### RateLimitInfo Properties

The `last_rate_limit` property contains a `RateLimitInfo` object with:

- **limit** (`int`): Maximum requests allowed in the current window
- **remaining** (`int`): Requests remaining before rate limit is hit
- **reset** (`datetime`): When the current rate limit window resets

```python
from datetime import datetime

with Pincho() as client:
    client.send('Test', 'Message')

    if client.last_rate_limit:
        # Calculate time until reset
        time_until_reset = client.last_rate_limit.reset - datetime.now()
        print(f"Rate limit resets in: {time_until_reset.total_seconds():.0f} seconds")
```

### Batch Sending with Rate Limit Awareness

```python
def send_batch_with_awareness(messages: list):
    """Send multiple messages with rate limit awareness."""
    with Pincho() as client:
        for title, message in messages:
            response = client.send(title, message)

            if client.last_rate_limit and client.last_rate_limit.remaining < 5:
                print(f"Pausing - only {client.last_rate_limit.remaining} requests remaining")
                # Wait until reset or implement custom logic
                break
```

## Retry-After Behavior

The library automatically handles rate limits with intelligent backoff:

### Automatic Retry

When you hit a rate limit (429 response), the library will:

1. Check for `Retry-After` header in the response
2. If present, wait the exact time specified by the server
3. If not present, use exponential backoff (5s, 10s, 20s...)
4. Automatically retry the request

```python
# Rate limits are handled automatically
with Pincho(max_retries=3) as client:
    # Even if rate limited, this will retry automatically
    response = client.send('Important', 'Message')
```

### Backoff Strategy

- **Rate limit errors (429)**: Uses Retry-After header or longer backoff (5s base)
- **Server errors (5xx)**: Standard exponential backoff (1s base)
- **Network errors**: Standard exponential backoff (1s base)
- **Maximum backoff**: 30 seconds (capped)

### Disabling Retries

```python
# Disable automatic retries
client = Pincho(max_retries=0)
```

## Logging Configuration

The library uses Python's standard `logging` module with the logger name `pincho`.

### Enable Debug Logging

```python
import logging

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or configure just pincho logger
logger = logging.getLogger('pincho')
logger.setLevel(logging.DEBUG)
```

### Log Levels

- **DEBUG**: Client initialization, retry attempts, request details, rate limit headers
- **INFO**: Successful notification sends
- **WARNING**: Retries due to errors, rate limit warnings
- **ERROR**: Final failures after all retries

### Example Log Output

```
DEBUG:pincho:AsyncPincho initialized with token=abc12345..., timeout=30.0, max_retries=3
DEBUG:pincho:Send attempt 1/4
DEBUG:pincho:Rate limit info: 95/100 remaining, resets at 2025-11-16 10:00:00
INFO:pincho:Notification sent successfully: Build Complete
```

### Custom Log Handler

```python
import logging

# Create custom handler
handler = logging.FileHandler('pincho.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add to pincho logger
logger = logging.getLogger('pincho')
logger.addHandler(handler)
```

## Async vs Sync Clients

### Sync Client (Pincho)

Best for:
- Simple scripts
- Single notifications
- Sequential operations
- When async isn't needed

```python
from pincho import Pincho

# Context manager (recommended)
with Pincho() as client:
    client.send('Title', 'Message')

# Manual cleanup
client = Pincho()
try:
    client.send('Title', 'Message')
finally:
    client.close()
```

### Async Client (AsyncPincho)

Best for:
- High-throughput applications
- Concurrent notifications
- Integration with async frameworks (FastAPI, aiohttp)
- Non-blocking operations

```python
import asyncio
from pincho import AsyncPincho

async def main():
    async with AsyncPincho() as client:
        # Single notification
        await client.send('Title', 'Message')

        # Concurrent notifications (much faster)
        tasks = [
            client.send(f'Alert {i}', f'Message {i}')
            for i in range(10)
        ]
        responses = await asyncio.gather(*tasks)

asyncio.run(main())
```

### Performance Comparison

```python
import time
import asyncio

# Sync: Sequential (slower)
with Pincho() as client:
    start = time.time()
    for i in range(10):
        client.send(f'Alert {i}', f'Message {i}')
    print(f"Sync: {time.time() - start:.2f}s")

# Async: Concurrent (faster)
async def async_send():
    async with AsyncPincho() as client:
        start = time.time()
        tasks = [client.send(f'Alert {i}', f'Message {i}') for i in range(10)]
        await asyncio.gather(*tasks)
        print(f"Async: {time.time() - start:.2f}s")

asyncio.run(async_send())
```

## Custom Configuration

### Environment Variables

Set defaults via environment variables:

```bash
export PINCHO_TOKEN="your_token_here"
export PINCHO_TIMEOUT="60"
export PINCHO_MAX_RETRIES="5"
```

```python
# Automatically picks up env vars
client = Pincho()
```

### Constructor Overrides

Explicit configuration takes precedence:

```python
client = Pincho(
    token='abc12345',      # Override PINCHO_TOKEN
    timeout=120.0,         # Request timeout (seconds)
    max_retries=10,        # Retry attempts (0 to disable)
)
```

### Custom Base URL (Testing)

```python
# For testing against mock server
client = Pincho(
    token='test_token',
    base_url='http://localhost:8080'
)
```

### Configuration Priority

1. Constructor parameter (highest priority)
2. Environment variable
3. Default value (lowest priority)

Example:
```python
# If PINCHO_TIMEOUT=30 in environment
client = Pincho(timeout=60)  # Uses 60, not 30
```

## Error Handling Patterns

### Distinguishing Error Types

```python
from pincho import (
    Pincho,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
)

try:
    with Pincho() as client:
        client.send('Alert', 'Message')
except AuthenticationError as e:
    # Invalid or revoked token
    print(f"Auth failed: {e}")
    # Not retryable - fix credentials
except ValidationError as e:
    # Bad parameters (missing title, invalid tags)
    print(f"Invalid request: {e}")
    # Not retryable - fix parameters
except RateLimitError as e:
    # Shouldn't happen with retries enabled
    print(f"Rate limited after retries: {e}")
    # Usually auto-retried
except ServerError as e:
    # API server issue
    print(f"Server error: {e}")
    # Usually auto-retried
except NetworkError as e:
    # Connection/timeout issues
    print(f"Network issue: {e}")
    # Usually auto-retried
```

### Checking Retryability

```python
from pincho.exceptions import PinchoError

try:
    client.send('Title', 'Message')
except PinchoError as e:
    if e.is_retryable:
        print("Error is retryable, consider waiting and retrying manually")
    else:
        print("Error is not retryable, fix the issue first")
```

## Integration Examples

### FastAPI Integration

```python
from fastapi import FastAPI, BackgroundTasks
from pincho import AsyncPincho

app = FastAPI()

async def send_notification(title: str, message: str):
    async with AsyncPincho() as client:
        await client.send(title, message)

@app.post("/deploy")
async def deploy(background_tasks: BackgroundTasks):
    # Process deployment...
    background_tasks.add_task(
        send_notification,
        "Deploy Complete",
        "v1.2.3 deployed successfully"
    )
    return {"status": "deployed"}
```

### Flask Integration

```python
from flask import Flask, request
from pincho import Pincho

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json

    with Pincho() as client:
        client.send(
            title=f"Webhook: {data['event']}",
            message=data['message'],
            type='webhook'
        )

    return {'status': 'ok'}
```

### Celery Task

```python
from celery import Celery
from pincho import Pincho

app = Celery('tasks')

@app.task
def send_notification_task(title: str, message: str, **kwargs):
    with Pincho() as client:
        return client.send(title, message, **kwargs)
```

## Best Practices

1. **Use context managers** - Ensures proper resource cleanup
2. **Monitor rate limits** - Check `last_rate_limit` for high-volume applications
3. **Enable logging in production** - At least INFO level for tracking
4. **Use async for concurrency** - Significant performance benefit for multiple notifications
5. **Handle errors appropriately** - Check `is_retryable` for custom retry logic
6. **Secure your tokens** - Use environment variables, never hardcode
