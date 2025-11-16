# WirePusher Python Library

Official Python client for [WirePusher](https://wirepusher.dev) push notifications.

## Installation

```bash
pip install wirepusher_official
```

## Quick Start

```python
from wirepusher_official import WirePusher

# Auto-load token from WIREPUSHER_TOKEN env var
with WirePusher() as client:
    client.send('Deploy Complete', 'Version 1.2.3 deployed')

# Or provide token explicitly
with WirePusher(token='YOUR_TOKEN') as client:
    client.send('Alert', 'Server CPU at 95%')
```

## Features

```python
# Full parameters
client.send(
    title='Deploy Complete',
    message='Version 1.2.3 deployed',
    type='deployment',
    tags=['production', 'backend'],
    image_url='https://example.com/success.png',
    action_url='https://example.com/deploy/123'
)

# AI-powered notifications (NotifAI)
response = client.notifai('deployment finished, v2.1.3 is live')
print(response.notification)  # AI-generated title, message, tags

# Encrypted messages
client.send(
    title='Security Alert',
    message='Sensitive data',
    type='security',
    encryption_password='your_password'
)

# Async support
from wirepusher_official import AsyncWirePusher

async with AsyncWirePusher() as client:
    await client.send('Test', 'Message')
```

## Configuration

```python
# Environment variables (recommended)
# WIREPUSHER_TOKEN - API token (required if not passed to constructor)
# WIREPUSHER_TIMEOUT - Request timeout in seconds (default: 30)
# WIREPUSHER_MAX_RETRIES - Retry attempts (default: 3)

# Or explicit configuration
client = WirePusher(
    token='abc12345',
    timeout=60.0,
    max_retries=5
)
```

## Error Handling

```python
from wirepusher_official import (
    WirePusher,
    AuthenticationError,
    ValidationError,
    RateLimitError
)

try:
    with WirePusher() as client:
        client.send('Title', 'Message')
except AuthenticationError:
    print("Invalid token")
except ValidationError:
    print("Invalid parameters")
except RateLimitError:
    print("Rate limited - auto-retry handled this")
```

Automatic retry with exponential backoff for network errors, 5xx, and 429 (rate limit).

## Links

- **Get Token**: App → Settings → Help → copy token
- **Documentation**: https://wirepusher.dev/help
- **Repository**: https://gitlab.com/wirepusher/wirepusher-python
- **PyPI**: https://pypi.org/project/wirepusher_official/

## License

MIT
