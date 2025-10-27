# WirePusher Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Official Python SDK for [WirePusher](https://wirepusher.com) push notifications API.

## Features

- ✅ **Simple & Pythonic API** - Clean, intuitive interface following Python best practices
- ✅ **Sync & Async Support** - Both synchronous and asynchronous clients with identical APIs
- ✅ **Type Hints** - Full type annotations for better IDE support and type checking
- ✅ **Context Managers** - Automatic resource cleanup with `with` statements
- ✅ **Modern** - Built with httpx, supports HTTP/2
- ✅ **Well-Tested** - 94% test coverage with comprehensive test suite
- ✅ **Zero Configuration** - Just install and use, no complex setup required

## Installation

```bash
pip install wirepusher
```

## Quick Start

### Synchronous Client

```python
from wirepusher import WirePusher

# Initialize client with your user ID (for personal notifications)
client = WirePusher(user_id='your_user_id')

# Send a simple notification
response = client.send('Build Complete', 'v1.2.3 deployed successfully')
print(response.status)  # 'success'

# Always close the client when done
client.close()
```

### Using Context Manager (Recommended)

```python
from wirepusher import WirePusher

with WirePusher(user_id='your_user_id') as client:
    client.send('Server Alert', 'CPU usage is at 90%')
    # Client automatically closed after exiting the context
```

### Async Client

```python
import asyncio
from wirepusher import AsyncWirePusher

async def send_notification():
    async with AsyncWirePusher(user_id='your_user_id') as client:
        response = await client.send('Build Complete', 'Deployment finished')
        print(response.status)

asyncio.run(send_notification())
```

### Advanced Usage

```python
from wirepusher import WirePusher

with WirePusher(user_id='your_user_id') as client:
    # Send notification with all optional parameters
    response = client.send(
        title='Deploy Complete',
        message='v1.2.3 deployed to production',
        type='deployment',
        tags=['production', 'release', 'v1.2.3'],
        image_url='https://example.com/deployment-success.png',
        action_url='https://example.com/deployment/123'
    )

    print(f"Status: {response.status}")
    print(f"Message: {response.message}")
```

## Authentication

WirePusher supports two authentication methods for sending notifications:

### Team Tokens (Recommended for Teams)

Team tokens (starting with `wpt_`) send notifications to ALL members of a team.

```python
from wirepusher import WirePusher

# Send to all team members
with WirePusher(token='wpt_abc123xyz...') as client:
    client.send('Team Alert', 'Server maintenance in 1 hour')
```

**Use cases:**
- Team-wide alerts and announcements
- Shared project notifications
- Collaborative workflows

### User ID (Personal Notifications)

User IDs send notifications to a specific user's devices only.

```python
from wirepusher import WirePusher

# Send to specific user
with WirePusher(user_id='user_abc123') as client:
    client.send('Personal Reminder', 'Your task is due tomorrow')
```

**Use cases:**
- Personal notifications
- User-specific alerts
- Individual reminders

**Note:** Team tokens and user IDs are mutually exclusive - use one or the other, not both.

## Encrypted Notifications

WirePusher supports AES-128-CBC encryption for secure message delivery. Only the message content is encrypted; metadata (title, type, tags) remains unencrypted for filtering and display.

### Setup

1. Create a notification type in the WirePusher app
2. Set an encryption password for that type
3. Use the same password when sending encrypted notifications

### Example

```python
from wirepusher import WirePusher

with WirePusher(user_id='your_user_id') as client:
    client.send(
        title='Secure Message',              # Not encrypted (for display)
        message='Sensitive information here', # Encrypted
        type='secure',                        # Must match app type with password
        encryption_password='your_password'   # Must match app configuration
    )
```

### What's Encrypted

- ✅ Message content only
- ❌ Title, type, tags, image_url, action_url (unencrypted for filtering/display)

### Security Notes

- Message content encrypted using AES-128-CBC
- 16-byte random IV generated for each message
- Password must match the type configuration in the app
- Use strong passwords (minimum 12 characters)
- Store passwords securely (environment variables, secret managers)

### Advanced Encryption Example

```python
from wirepusher import WirePusher
import os

# Store password in environment variable
encryption_password = os.getenv('WIREPUSHER_ENCRYPTION_PASSWORD')

with WirePusher(user_id='your_user_id') as client:
    # Send encrypted notification
    response = client.send(
        title='Security Alert',
        message='Unauthorized access attempt detected from IP 192.168.1.100',
        type='security',
        tags=['critical', 'security'],
        encryption_password=encryption_password
    )

    print(f"Encrypted notification sent: {response.status}")
```

## API Reference

### `WirePusher` (Synchronous Client)

Initialize a synchronous WirePusher client.

**Parameters:**
- `token` (str, optional): WirePusher team token (mutually exclusive with `user_id`)
- `user_id` (str, optional): WirePusher user ID (mutually exclusive with `token`)
- `timeout` (float, optional): Request timeout in seconds (default: 30.0)
- `base_url` (str, optional): Custom base URL (mainly for testing)

**Note:** You must specify either `token` OR `user_id`, not both.

**Methods:**

#### `send(title, message, **kwargs)`

Send a notification via WirePusher API.

**Parameters:**
- `title` (str, required): Notification title (max 250 characters)
- `message` (str, required): Notification message body (max 10,000 characters)
- `type` (str, optional): Notification type for filtering/organization
- `tags` (list[str], optional): List of tags (max 10 tags, max 50 characters each)
- `image_url` (str, optional): Image URL to display with notification
- `action_url` (str, optional): URL to open when notification is tapped
- `encryption_password` (str, optional): Password for AES-128-CBC encryption (must match type configuration in app)

**Returns:**
- `NotificationResponse`: Object with `status` and `message` fields

**Raises:**
- `AuthenticationError`: Invalid token or user ID
- `ValidationError`: Invalid parameters (missing required fields, etc.)
- `WirePusherError`: Other API errors (network issues, server errors, etc.)

#### `close()`

Close the HTTP client and release resources.

### `AsyncWirePusher` (Asynchronous Client)

Initialize an asynchronous WirePusher client. Has the same parameters and methods as `WirePusher`, but all methods are async.

**Example:**
```python
async with AsyncWirePusher(user_id='user_id') as client:
    response = await client.send('Title', 'Message')
```

## Error Handling

The SDK provides three exception types:

```python
from wirepusher import WirePusher
from wirepusher.exceptions import (
    WirePusherError,
    AuthenticationError,
    ValidationError
)

try:
    with WirePusher(user_id='user123') as client:
        client.send('Test', 'Message')
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except WirePusherError as e:
    print(f"API error: {e}")
```

### Exception Hierarchy

- `WirePusherError` - Base exception for all SDK errors
  - `AuthenticationError` - Invalid credentials or forbidden access (401, 403 errors)
  - `ValidationError` - Invalid parameters or user not found (400, 404 errors)

## Use Cases

### CI/CD Pipelines

```python
from wirepusher import WirePusher

def notify_build_status(status, details):
    with WirePusher(user_id='user_id') as client:
        title = f"Build {status}"
        client.send(
            title=title,
            message=details,
            type='ci/cd',
            tags=['build', status.lower()]
        )

# In your CI/CD pipeline
notify_build_status('PASSED', 'All tests passed on main branch')
```

### Server Monitoring

```python
import psutil
from wirepusher import WirePusher

def check_server_health():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    if cpu > 80 or memory > 80:
        with WirePusher(user_id='user_id') as client:
            client.send(
                title='Server Alert',
                message=f'CPU: {cpu}%, Memory: {memory}%',
                type='alert',
                tags=['server', 'critical']
            )
```

### Data Pipeline Notifications

```python
import asyncio
from wirepusher import AsyncWirePusher

async def process_data_pipeline():
    # Your data processing logic here
    records_processed = 10000

    async with AsyncWirePusher(user_id='user_id') as client:
        await client.send(
            title='ETL Job Complete',
            message=f'Processed {records_processed:,} records',
            type='etl',
            tags=['data-pipeline', 'success']
        )

asyncio.run(process_data_pipeline())
```

### Flask/Django Integration

```python
from flask import Flask
from wirepusher import WirePusher

app = Flask(__name__)

@app.route('/deploy', methods=['POST'])
def deploy():
    # Deployment logic here

    with WirePusher(user_id='user_id') as client:
        client.send(
            title='Deployment Started',
            message='Deploying application to production',
            type='deployment'
        )

    return {'status': 'deploying'}
```

## Getting Your Credentials

1. Download the WirePusher app (iOS/Android)
2. Create an account
3. Go to Settings → API Tokens
4. Create a new token
5. Note your User ID and Token

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://gitlab.com/wirepusher/python-sdk.git
cd python-sdk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=wirepusher --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Type checking
mypy src/wirepusher

# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/

# Run all quality checks
mypy src/wirepusher && black --check src/ tests/ && ruff check src/ tests/
```

## Requirements

- Python 3.8 or higher
- httpx >= 0.24.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Repository**: https://gitlab.com/wirepusher/python-sdk
- **Issues**: https://gitlab.com/wirepusher/python-sdk/-/issues
- **WirePusher App**: https://wirepusher.com

## Support

For SDK issues, please open an issue on [GitLab](https://gitlab.com/wirepusher/python-sdk/-/issues).

For WirePusher app support, visit the [WirePusher website](https://wirepusher.com).
