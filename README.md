# WirePusher Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Official Python SDK for [WirePusher](https://wirepusher.dev) push notifications.

## Features

- ✅ **Simple & Pythonic** - Clean interface following Python best practices
- ✅ **Sync & Async** - Both synchronous and asynchronous clients
- ✅ **Type Hints** - Full type annotations for IDE support
- ✅ **Context Managers** - Automatic resource cleanup
- ✅ **Modern** - Built with httpx, supports HTTP/2
- ✅ **Well-Tested** - 94% test coverage

## Installation

```bash
pip install wirepusher
```

## Quick Start

```python
from wirepusher import WirePusher

# Initialize with your token
with WirePusher(token='wpu_YOUR_TOKEN') as client:
    client.send(
        title='Deploy Complete',
        message='Version 1.2.3 deployed to production'
    )
```

**Get your token:** Open app → Settings → Help → copy token

## Usage

### Basic Example

```python
from wirepusher import WirePusher

with WirePusher(token='wpu_abc123xyz') as client:
    response = client.send(
        title='Deploy Complete',
        message='Version 1.2.3 deployed to production'
    )
    print(response.status)  # 'success'
```

### All Parameters

```python
from wirepusher import WirePusher

with WirePusher(token='wpu_abc123xyz') as client:
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
    async with AsyncWirePusher(token='wpu_abc123xyz') as client:
        response = await client.send(
            title='Deploy Complete',
            message='Version 1.2.3 deployed to production'
        )
        print(response.status)

asyncio.run(send_notification())
```

## Encryption

Encrypt notification messages using AES-128-CBC. Only the `message` field is encrypted—`title`, `type`, `tags`, `image_url`, and `action_url` remain unencrypted for filtering and display.

**Setup:**
1. In the app, create a notification type
2. Set an encryption password for that type
3. Pass the same `type` and password when sending

```python
from wirepusher import WirePusher
import os

encryption_password = os.getenv('WIREPUSHER_ENCRYPTION_PASSWORD')

with WirePusher(token='wpu_abc123xyz') as client:
    response = client.send(
        title='Security Alert',
        message='Unauthorized access attempt detected',
        type='security',
        encryption_password=encryption_password
    )
```

**Security notes:**
- Use strong passwords (minimum 12 characters)
- Store passwords securely (environment variables, secret managers)
- Password must match the type configuration in the app

## API Reference

### WirePusher / AsyncWirePusher

**Constructor Parameters:**
- `token` (str, required): Your WirePusher token (starts with `wpu_` or `wpt_`)
- `timeout` (float, optional): Request timeout in seconds (default: 30.0)
- `base_url` (str, optional): Custom base URL for testing

### send()

Send a notification.

**Parameters:**
- `title` (str, required): Notification title
- `message` (str, required): Notification message
- `type` (str, optional): Category for organization
- `tags` (list[str], optional): Tags for filtering
- `image_url` (str, optional): Image URL to display
- `action_url` (str, optional): URL to open when tapped
- `encryption_password` (str, optional): Password for encryption

**Returns:**
- `NotificationResponse`: Object with `status` and `message` fields

**Raises:**
- `AuthenticationError`: Invalid token (401, 403)
- `ValidationError`: Invalid parameters (400, 404)
- `WirePusherError`: Other API errors

## Error Handling

```python
from wirepusher import WirePusher
from wirepusher.exceptions import (
    WirePusherError,
    AuthenticationError,
    ValidationError
)

try:
    with WirePusher(token='wpu_abc123xyz') as client:
        client.send('Deploy Complete', 'Version 1.2.3 deployed')
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except WirePusherError as e:
    print(f"API error: {e}")
```

## Examples

### CI/CD Pipeline

```python
from wirepusher import WirePusher
import os

def notify_deployment(version, environment):
    token = os.getenv('WIREPUSHER_TOKEN')

    with WirePusher(token=token) as client:
        client.send(
            title='Deploy Complete',
            message=f'Version {version} deployed to {environment}',
            type='deployment',
            tags=[environment, version]
        )

# In your CI/CD script
notify_deployment('1.2.3', 'production')
```

### Server Monitoring

```python
import psutil
from wirepusher import WirePusher
import os

def check_server_health():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent

    if cpu > 80 or memory > 80:
        token = os.getenv('WIREPUSHER_TOKEN')
        with WirePusher(token=token) as client:
            client.send(
                title='Server Alert',
                message=f'CPU: {cpu}%, Memory: {memory}%',
                type='alert',
                tags=['server', 'critical']
            )
```

### Flask Integration

```python
from flask import Flask, request
from wirepusher import WirePusher
import os

app = Flask(__name__)

@app.route('/deploy', methods=['POST'])
def deploy():
    version = request.json.get('version')

    # Your deployment logic here

    token = os.getenv('WIREPUSHER_TOKEN')
    with WirePusher(token=token) as client:
        client.send(
            title='Deploy Complete',
            message=f'Version {version} deployed to production',
            type='deployment'
        )

    return {'status': 'success'}
```

### Data Pipeline

```python
import asyncio
from wirepusher import AsyncWirePusher
import os

async def process_data_pipeline():
    # Your data processing logic
    records_processed = 10000

    token = os.getenv('WIREPUSHER_TOKEN')
    async with AsyncWirePusher(token=token) as client:
        await client.send(
            title='ETL Job Complete',
            message=f'Processed {records_processed:,} records',
            type='etl',
            tags=['data-pipeline', 'success']
        )

asyncio.run(process_data_pipeline())
```

## Development

### Setup

```bash
# Clone repository
git clone https://gitlab.com/wirepusher/python-sdk.git
cd python-sdk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run tests with coverage
pytest --cov=wirepusher --cov-report=term-missing

# Type checking
mypy src/wirepusher

# Formatting
black src/ tests/

# Linting
ruff check src/ tests/
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
