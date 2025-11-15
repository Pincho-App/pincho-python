# WirePusher Python Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Official Python client library for [WirePusher](https://wirepusher.dev) push notifications.

## Features

- ✅ **Simple & Pythonic** - Clean interface following Python best practices
- ✅ **Sync & Async** - Both synchronous and asynchronous clients
- ✅ **AI-Powered** - NotifAI endpoint for generating notifications from text
- ✅ **Automatic Retries** - Exponential backoff with smart error handling
- ✅ **Modern & Typed** - Built with httpx (HTTP/2), full type hints

## Quick Start

```bash
pip install wirepusher
```

```python
from wirepusher import WirePusher

# Initialize with your token
with WirePusher(token='YOUR_TOKEN') as client:
    client.send(
        title='Deploy Complete',
        message='Version 1.2.3 deployed to production'
    )
```

**Get your token:** Open app → Settings → Help → copy token

## Usage

### All Parameters

```python
from wirepusher import WirePusher

with WirePusher(token='abc12345') as client:
    response = client.send(
        title='Deploy Complete',
        message='Version 1.2.3 deployed to production',
        type='deployment',
        tags=['production', 'backend'],
        image_url='https://cdn.example.com/success.png',
        action_url='https://dash.example.com/deploy/123'
    )
```

### Async Client

```python
import asyncio
from wirepusher import AsyncWirePusher

async def send_notification():
    async with AsyncWirePusher(token='abc12345') as client:
        response = await client.send(
            title='Deploy Complete',
            message='Version 1.2.3 deployed to production'
        )
        print(response.status)

asyncio.run(send_notification())
```

### NotifAI - AI-Powered Notifications

Let AI generate structured notifications from free-form text using Gemini:

```python
from wirepusher import WirePusher

with WirePusher(token='abc12345') as client:
    response = client.notifai(
        'deployment finished successfully, v2.1.3 is live on prod'
    )
    print(response.notification)  # AI-generated title, message, tags
```

The AI automatically generates:
- Title and message
- Relevant tags
- Action URL (when applicable)

Override the AI-generated type:

```python
response = client.notifai(
    'cpu at 95% on web-3',
    type='alert'  # Override AI type
)
```

### Automatic Retries

The library automatically retries failed requests with exponential backoff (default: 3 retries). Retries network errors, 5xx errors, and 429 (rate limit). Client errors (400, 401, 403, 404) are not retried.

```python
# Configure retries
client = WirePusher(token='abc12345', max_retries=5)  # Custom
client = WirePusher(token='abc12345', max_retries=0)  # Disable
```

### Debug Logging

Enable debug logging using Python's standard `logging` module:

```python
import logging
from wirepusher import WirePusher

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

with WirePusher(token='abc12345') as client:
    client.send('Test', 'Message')  # Shows retry attempts, request details

# Output:
# DEBUG:wirepusher:AsyncWirePusher initialized with token=abc12345...
# DEBUG:wirepusher:Send attempt 1/4
# INFO:wirepusher:Notification sent successfully: Test
```

## Encryption

Encrypt notification messages using AES-128-CBC. Only the `message` is encrypted—`title`, `type`, and `tags` remain visible for filtering.

```python
# 1. In app: create notification type with encryption password
# 2. Send with matching type and password
with WirePusher(token='abc12345') as client:
    client.send(
        title='Security Alert',
        message='Sensitive data here',
        type='security',
        encryption_password=os.getenv('ENCRYPTION_PASSWORD')
    )
```

## API Reference

### WirePusher / AsyncWirePusher

**Constructor Parameters:**
- `token` (str, required): Your WirePusher token (8-character alphanumeric string)
- `timeout` (float, optional): Request timeout in seconds (default: 30.0)
- `max_retries` (int, optional): Maximum retry attempts (default: 3, set to 0 to disable)
- `base_url` (str, optional): Custom base URL for testing

### send()

Send a notification.

**Parameters:**
- `title` (str, required): Notification title
- `message` (str, optional): Notification message
- `type` (str, optional): Category for organization
- `tags` (list[str], optional): Tags for filtering (automatically normalized)
- `image_url` (str, optional): Image URL to display
- `action_url` (str, optional): URL to open when tapped
- `encryption_password` (str, optional): Password for encryption

**Returns:**
- `NotificationResponse`: Object with `status` and `message` fields

**Raises:**
- `AuthenticationError`: Invalid token (401, 403)
- `ValidationError`: Invalid parameters (400, 404)
- `RateLimitError`: Rate limit exceeded (429)
- `ServerError`: Server error (5xx)
- `NetworkError`: Network/timeout error
- `WirePusherError`: Other API errors

### notifai()

Generate AI-powered notification from free-form text.

**Parameters:**
- `text` (str, required): Free-form text to convert
- `type` (str, optional): Override AI-generated type

**Returns:**
- `NotifAIResponse`: Object with `status`, `message`, and `notification` fields

**Raises:**
- Same exceptions as `send()`

## Error Handling

```python
from wirepusher import WirePusher, AuthenticationError, ValidationError

try:
    with WirePusher(token='abc12345') as client:
        client.send('Title', 'Message')
except AuthenticationError:
    print("Invalid token")
except ValidationError:
    print("Invalid parameters")
except Exception as e:
    print(f"Error: {e}")  # Auto-retry handles transient errors
```

**Exceptions:** `AuthenticationError`, `ValidationError`, `RateLimitError`, `ServerError`, `NetworkError`

## Validation Philosophy

This library performs **minimal client-side validation** to ensure the API remains the source of truth:

### ✅ We Validate

- **Required parameters**: `title` and `token`
- **Parameter types**: Ensuring correct Python types

### ✅ We Normalize

- **Tags**: Lowercase conversion, whitespace trimming, deduplication, and invalid character filtering
- **Silent filtering**: Invalid tags are filtered out (not rejected)

### ❌ We Don't Validate

- **Message**: Optional parameter (not required by API)
- **Tag limits**: API validates max 10 tags, 50 characters each
- **Business rules**: Rules that may change server-side

### Why This Approach?

**The API is the source of truth.** Client-side validation of business rules can create false negatives when API rules evolve independently of client library updates. By performing minimal validation:

- ✅ Valid requests are never rejected due to outdated client logic
- ✅ API error messages provide detailed context (error codes, param names)
- ✅ Less maintenance burden across client libraries
- ✅ Consistent behavior as API evolves

The API returns comprehensive error responses with `type`, `code`, `message`, and `param` fields to help you debug validation failures.

## Examples

### CI/CD Pipeline

```python
from wirepusher import WirePusher

def notify_deployment(version, environment):
    with WirePusher(token=os.getenv('WIREPUSHER_TOKEN')) as client:
        client.send(
            title='Deploy Complete',
            message=f'Version {version} deployed to {environment}',
            type='deployment',
            tags=[environment, version]
        )
```

### Server Monitoring

```python
from wirepusher import WirePusher
import psutil

def check_server_health():
    cpu, memory = psutil.cpu_percent(), psutil.virtual_memory().percent
    if cpu > 80 or memory > 80:
        with WirePusher(token=os.getenv('WIREPUSHER_TOKEN')) as client:
            client.send(
                title='Server Alert',
                message=f'CPU: {cpu}%, Memory: {memory}%',
                type='alert',
                tags=['critical']
            )
```

## Development

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# Test
pytest --cov=wirepusher
mypy src/wirepusher
```

## Requirements

- Python 3.8+
- httpx >= 0.24.0

## Links

- **Documentation**: https://wirepusher.dev/help
- **Repository**: https://gitlab.com/wirepusher/python-sdk
- **Issues**: https://gitlab.com/wirepusher/python-sdk/-/issues
- **PyPI**: https://pypi.org/project/wirepusher/

## License

MIT License - see [LICENSE](LICENSE) file for details.
