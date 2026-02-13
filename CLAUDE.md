# CLAUDE.md - Pincho Python Library

Context file for AI-powered development assistance on the Pincho Python library project.

## Project Overview

**Pincho Python Library** is a Python client library for sending push notifications via [Pincho](https://pincho.app).

- **Language**: Python 3.8+
- **Framework**: httpx (HTTP client with HTTP/2 support)
- **Purpose**: Send notifications from Python applications, scripts, and services
- **Philosophy**: Simple, Pythonic, zero unnecessary dependencies

## Architecture

```
pincho-python/
├── src/pincho/          # Main library code
│   ├── __init__.py          # Public API exports
│   ├── client.py            # Synchronous client (wraps async)
│   ├── async_client.py      # Asynchronous client (main implementation)
│   ├── models.py            # Data models (Request/Response)
│   ├── exceptions.py        # Custom exceptions
│   ├── validation.py        # Input validation utilities
│   ├── crypto.py            # AES-128-CBC encryption
│   └── py.typed             # Type hints marker
├── tests/                   # Test suite (pytest)
│   ├── test_client.py       # Sync client tests
│   ├── test_async_client.py # Async client tests
│   ├── test_crypto.py       # Encryption tests
│   ├── test_validation.py   # Validation tests
│   └── conftest.py          # Pytest fixtures
├── examples/                # Usage examples
├── docs/                    # Documentation
└── pyproject.toml           # Modern Python packaging

```

## Key Features

### 1. Dual Client Architecture

**AsyncPincho** (Primary Implementation):
- Full async/await support with asyncio
- Main implementation with all features
- Context manager support (`async with`)

**Pincho** (Sync Wrapper):
- Synchronous API wrapping AsyncPincho
- Uses `asyncio.run()` internally
- Same API as async client

This follows modern Python library patterns (like httpx).

### 2. API Endpoints

**send()** - Send notifications:
```python
client.send(
    title='Deploy Complete',
    message='v1.2.3 deployed',
    type='deployment',
    tags=['production', 'release'],
    image_url='https://example.com/image.png',
    action_url='https://example.com/action',
    encryption_password='secret'  # Optional
)
```

**notifai()** - AI-powered notifications:
```python
client.notifai(
    'deployment finished successfully, v2.1.3 is live on prod',
    type='deployment'  # Optional override
)
```

### 3. Automatic Retry Logic

- **Default**: 3 retries with exponential backoff (1s, 2s, 4s, 8s)
- **Configurable**: `max_retries` parameter (0 to disable)
- **Retryable errors**: Network errors, 5xx, 429 (rate limit)
- **Non-retryable**: 400, 401, 403, 404 (client errors)
- **Rate limit handling**: Special backoff (5s, 10s, 20s)

Implementation: `_send_with_retry()` and `_notifai_with_retry()` in `async_client.py`

### 4. Error Categorization

All exceptions have `is_retryable` property:

- `AuthenticationError` (401, 403) → `is_retryable = False`
- `ValidationError` (400, 404) → `is_retryable = False`
- `RateLimitError` (429) → `is_retryable = True`
- `ServerError` (5xx) → `is_retryable = True`
- `NetworkError` (network/timeout) → `is_retryable = True`

### 5. Tag Normalization

Automatic validation and normalization:
- Lowercase conversion
- Whitespace trimming
- Duplicate removal (case-insensitive)
- Character validation (alphanumeric, hyphens, underscores only)
- Invalid tags filtered out

Implementation: `validation.py`

### 6. Logging Integration

Uses Python's standard `logging` module (zero dependencies):

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Shows:
# DEBUG:pincho:AsyncPincho initialized with token=abc12345...
# DEBUG:pincho:Send attempt 1/4
# INFO:pincho:Notification sent successfully: Deploy Complete
```

Levels:
- **DEBUG**: Initialization, retry attempts, request details
- **INFO**: Successful sends
- **WARNING**: Retries, rate limits
- **ERROR**: Final failures

### 7. Encryption

**AES-128-CBC** encryption matching mobile app:
- SHA1-based key derivation (for app compatibility)
- Custom Base64 encoding (URL-safe: `-` `_` `.` instead of `+` `/` `=`)
- Encrypts title, message, imageURL, actionURL (type, tags remain visible)
- Password must match type configuration in app

Implementation: `crypto.py`

## Configuration Priority

Environment variable support with constructor-based overrides:

```python
# Auto-load from environment variables
client = Pincho()  # reads PINCHO_TOKEN

# Explicit token
client = Pincho(token='abc12345')

# All options
client = Pincho(
    token='abc12345',     # Or PINCHO_TOKEN env var
    timeout=60.0,         # Or PINCHO_TIMEOUT env var (seconds), default: 30.0
    max_retries=5,        # Or PINCHO_MAX_RETRIES env var, default: 3
    base_url='...'        # Custom base URL (for testing)
)
```

**Environment Variables**:
- `PINCHO_TOKEN` - API token (required if not passed to constructor)
- `PINCHO_TIMEOUT` - Request timeout in seconds (default: 30)
- `PINCHO_MAX_RETRIES` - Maximum retry attempts (default: 3)

No config file support (not standard for Python libraries).

## Dependencies

**Runtime** (minimal):
- `httpx >= 0.24.0` - HTTP client with HTTP/2
- `cryptography >= 41.0.0` - AES encryption

**Development**:
- `pytest >= 7.0.0` - Testing framework
- `pytest-asyncio >= 0.21.0` - Async test support
- `pytest-cov >= 4.0.0` - Coverage reporting
- `pytest-httpx >= 0.22.0` - HTTP mocking
- `mypy >= 1.0.0` - Type checking (strict mode)
- `black >= 23.0.0` - Code formatting
- `ruff >= 0.1.0` - Linting

## Recent Changes

### v1.0.0 (Current - Alpha)

**Fixed**:
- Error parsing now handles nested API error format
- Parse `error.message`, `error.code`, `error.type`, `error.param` from API responses
- Build descriptive error messages with code and param context

### v2.0.0

**Added**:
- NotifAI endpoint for AI-powered notifications
- Automatic retry logic with exponential backoff
- Enhanced error categorization (`RateLimitError`, `ServerError`, `NetworkError`)
- Tag normalization and validation
- Python logging integration
- `max_retries` configuration parameter

**Changed**:
- **BREAKING**: Removed `device_id`/`user_id` authentication (token-only)
- Sync client now wraps async client (modern pattern)

**Technical**:
- New `validation.py` module
- Enhanced exception hierarchy
- Async-first implementation
- Comprehensive validation tests

## Development

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[dev]"
```

### Testing

```bash
pytest                          # All tests
pytest -v                       # Verbose
pytest --cov=pincho         # With coverage
pytest tests/test_client.py     # Specific file
pytest -k "test_retry"          # Specific tests
```

### Code Quality

```bash
mypy src/pincho             # Type checking (strict mode)
black src/ tests/               # Formatting
ruff check src/ tests/          # Linting
```

### Type Checking

Full type hints with `mypy` strict mode:
- All functions have type hints
- `py.typed` marker for IDE support
- Strict null checking
- No implicit optional

## Common Development Tasks

### Adding a Feature

1. Implement in `async_client.py` (async version)
2. Sync wrapper automatically gets it via `_run_async()`
3. Add tests in `tests/test_async_client.py`
4. Update README with examples
5. Add to CHANGELOG

### Adding an Exception

1. Add to `exceptions.py`
2. Set `is_retryable` class attribute
3. Update `_handle_http_error()` in async_client
4. Export in `__init__.py`
5. Update README error handling section

### Adding Validation

1. Add logic to `validation.py`
2. Write comprehensive tests in `tests/test_validation.py`
3. Integrate into client (`async_client.py`)
4. Document behavior in README

## Testing Philosophy

- **Unit tests**: Test functions in isolation
- **Mock HTTP**: Use `pytest-httpx` for HTTP mocking
- **Async tests**: Use `pytest-asyncio`
- **Type checking**: Run `mypy` in strict mode
- **Coverage target**: 95%+ for critical paths

## API Integration

### Endpoints

- `POST /send` - Send notifications
- `POST /notifai` - AI-generated notifications

### Authentication

Token via `token` parameter only (no config file).

### Response Format

**Success response:**
```json
{
  "status": "success",
  "message": "Notification sent successfully"
}
```

**Error response:**
```json
{
  "status": "error",
  "error": {
    "type": "validation_error",
    "code": "missing_required_field",
    "message": "Title is required",
    "param": "title"
  }
}
```

The library expects and parses only the nested error format. It extracts error details and builds descriptive error messages:
- `error.message` - Human-readable error message
- `error.code` - Machine-readable error code (appended in brackets)
- `error.type` - Error category (authentication_error, validation_error, etc.)
- `error.param` - Parameter that caused the error (appended in parentheses)

Example: `Invalid parameters: Title is required [missing_required_field] (parameter: title)`

## Notes for AI Assistants

- **Simplicity is key**: Keep API as simple as the Pincho app
- **Pythonic**: Follow PEP 8, use type hints, clear docstrings
- **Async-first**: Implement in `AsyncPincho`, sync wraps async
- **Zero config**: No config files (not standard for libraries)
- **Minimal deps**: Only httpx and cryptography for runtime
- **Logging**: Use stdlib `logging` module (not print statements)
- **Type hints**: Always include for all functions
- **Test coverage**: Aim for 95%+ on critical paths
- **Documentation**: Update README for user-facing changes
- **Consistency**: Match CLI features when applicable

## Project Status

**Current**: Production-ready v2.0.0 with comprehensive feature set

**Completed**:
- ✅ NotifAI endpoint
- ✅ Automatic retry logic
- ✅ Enhanced error categorization
- ✅ Tag normalization
- ✅ Python logging
- ✅ Token-only auth (removed device_id)
- ✅ Comprehensive documentation
- ✅ Async-first architecture

**Not Needed**:
- ❌ Config file support (not standard for libraries)
- ❌ CLI tool (separate pincho-cli project)

## Links

- **Repository**: https://github.com/Pincho-App/pincho-python
- **Issues**: https://github.com/Pincho-App/pincho-python/issues
- **API Docs**: https://pincho.app/help
- **App**: https://pincho.app
