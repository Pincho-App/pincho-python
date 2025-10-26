# WirePusher SDK Examples

This directory contains practical examples demonstrating how to use the WirePusher Python SDK in various scenarios.

## Running the Examples

First, set your credentials as environment variables:

```bash
export WIREPUSHER_TOKEN="wpt_your_token_here"
export WIREPUSHER_USER_ID="your_user_id_here"
```

Or on Windows:
```cmd
set WIREPUSHER_TOKEN=wpt_your_token_here
set WIREPUSHER_USER_ID=your_user_id_here
```

## Available Examples

### `basic_example.py`
Demonstrates basic usage of the synchronous client with simple and advanced notifications.

```bash
python examples/basic_example.py
```

### `async_example.py`
Shows how to use the asynchronous client, including concurrent notification sending.

```bash
python examples/async_example.py
```

### `flask_example.py`
Flask web application integration showing how to send notifications from HTTP endpoints.

Requires Flask:
```bash
pip install flask
python examples/flask_example.py
```

Then try these curl commands:
```bash
# Send a custom notification
curl -X POST http://localhost:5000/notify \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","message":"Hello from Flask!"}'

# Simulate a deployment
curl -X POST http://localhost:5000/deploy \
  -H "Content-Type: application/json" \
  -d '{"version":"v1.2.3","environment":"production"}'
```

## Common Use Cases

- **CI/CD Pipelines**: Notify on build/deploy status
- **Server Monitoring**: Alert on high CPU/memory usage
- **Data Pipelines**: Update on ETL job completion
- **Web Applications**: Send notifications from Flask/Django apps
- **Automation Scripts**: Notify on script completion or errors
