# Pincho Python Examples

This directory contains practical examples demonstrating various features of the Pincho Python library.

## Prerequisites

Before running examples:

1. **Install the library**:
   ```bash
   pip install pincho
   ```

2. **Set your API token**:
   ```bash
   export PINCHO_TOKEN="your_token_here"
   ```

3. **Get your token**: Open Pincho app → Settings → Help → copy token

## Examples Overview

### basic_example.py

**Use case**: Simple notification sending

**Demonstrates**:
- Context manager usage (recommended pattern)
- Basic notification with title and message
- Full notification with all optional parameters (type, tags, image_url, action_url)
- Response handling

**Run**:
```bash
python3 basic_example.py
```

---

### async_example.py

**Use case**: High-performance async/await operations

**Demonstrates**:
- AsyncPincho client usage
- Async context manager pattern
- Single async notification
- Concurrent notification sending with `asyncio.gather()` (10x faster than sequential)

**Run**:
```bash
python3 async_example.py
```

---

### encryption.py

**Use case**: Secure notifications with encrypted messages

**Demonstrates**:
- AES-128-CBC message encryption
- Setting encryption password (must match app configuration)
- What gets encrypted (message only) vs. what stays readable (title, type, tags)
- Multiple encryption scenarios

**Prerequisites**: Set encryption password:
```bash
export PINCHO_ENCRYPTION_PASSWORD="your_password"
```

**Run**:
```bash
python3 encryption.py
```

---

### notifai_example.py

**Use case**: AI-powered notification generation

**Demonstrates**:
- NotifAI endpoint for free-form text to structured notifications
- Automatic title, message, and tags generation using Gemini AI
- Type override capability
- Various use cases: deployments, system alerts, business events

**Run**:
```bash
python3 notifai_example.py
```

---

### flask_webhook.py

**Use case**: Server-side notification sending from web applications

**Demonstrates**:
- Flask webhook handler pattern
- Sending notifications in response to HTTP requests
- Background notification sending
- Error handling in web context

**Run**:
```bash
pip install flask
python3 flask_webhook.py
# Then test with: curl -X POST http://localhost:5000/webhook -H "Content-Type: application/json" -d '{"event": "deploy", "message": "v1.2.3"}'
```

---

### rate_limits.py

**Use case**: Monitoring API rate limits

**Demonstrates**:
- Accessing `last_rate_limit` property after requests
- Proactive rate limit checking
- Rate limit awareness patterns
- Best practices for high-volume applications

**Run**:
```bash
python3 rate_limits.py
```

## Common Patterns

### Environment Variable Configuration

```bash
# Required
export PINCHO_TOKEN="abc12345"

# Optional overrides
export PINCHO_TIMEOUT="60"        # Request timeout in seconds
export PINCHO_MAX_RETRIES="5"     # Retry attempts
```

### Error Handling

```python
from pincho import (
    Pincho,
    AuthenticationError,
    ValidationError,
    RateLimitError,
)

try:
    with Pincho() as client:
        client.send('Title', 'Message')
except AuthenticationError:
    print("Check your token")
except ValidationError:
    print("Check your parameters")
except RateLimitError:
    print("Rate limited (auto-retry failed)")
```

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all Pincho operations will log details
```

## Running All Examples

```bash
# Run each example (make sure PINCHO_TOKEN is set)
python3 basic_example.py
python3 async_example.py
python3 notifai_example.py
python3 rate_limits.py

# For encryption example, also set:
export PINCHO_ENCRYPTION_PASSWORD="your_password"
python3 encryption.py

# For Flask example:
pip install flask
python3 flask_webhook.py
```

## Need Help?

- **Library Documentation**: See main [README.md](../README.md)
- **Advanced Usage**: See [docs/ADVANCED.md](../docs/ADVANCED.md)
- **API Reference**: https://pincho.dev/help
- **Issues**: https://gitlab.com/pincho/pincho-python/-/issues
