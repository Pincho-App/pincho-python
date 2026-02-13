# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **NotifAI endpoint**: AI-powered notification generation using Gemini
  - `notifai()` method for both sync and async clients
  - Automatically generates title, message, tags, and action URL from free-form text
  - Optional type override parameter
- **Automatic retry logic** with exponential backoff
  - Default: 3 retries (1s, 2s, 4s, 8s delays)
  - Configurable via `max_retries` parameter
  - Special handling for rate limits (5s, 10s, 20s delays)
  - Retries on: network errors, 5xx errors, 429 (rate limit)
  - Does not retry: 400, 401, 403, 404 (client errors)
- **Enhanced error categorization**
  - New exceptions: `RateLimitError`, `ServerError`, `NetworkError`
  - `is_retryable` property on all exceptions
  - Better error messages with actionable suggestions
- **Tag normalization and validation**
  - Automatic lowercase conversion
  - Whitespace trimming
  - Duplicate removal (case-insensitive)
  - Character validation (alphanumeric, hyphens, underscores only)
- **Python logging integration**
  - Uses standard `logging` module (zero dependencies)
  - DEBUG, INFO, WARNING, ERROR levels
  - Shows: initialization, retry attempts, request progress, errors
- **Comprehensive documentation updates**
  - Updated README with NotifAI, retry logic, and logging sections
  - Enhanced API reference
  - Improved error handling guide
  - Python-adapted CONTRIBUTING.md (concise, 162 lines)
  - Updated CODE_OF_CONDUCT.md (concise, 48 lines)

### Changed
- **BREAKING**: Removed deprecated `device_id` / `user_id` authentication
  - Use `token` parameter only (simpler API)
  - Constructor now requires `token` parameter
- **Sync client architecture**: Now a lightweight wrapper around async client
  - Follows modern Python library patterns (like httpx)
  - Reduces code duplication
  - Easier to maintain

### Technical Improvements
- New `validation.py` module for input validation
- Enhanced exception hierarchy with retry categorization
- Async-first implementation (sync wraps async)
- Improved type hints throughout
- Added validation tests (comprehensive tag normalization tests)

### Migration Guide
If upgrading from v1.0.0:

**Before (v1.0.0):**
```python
# Old: device_id or user_id parameter
client = Pincho(user_id='user_abc123')
client = Pincho(device_id='device_abc123')  # deprecated
```

**After (v2.0.0):**
```python
# New: token-only authentication
client = Pincho(token='abc12345')
```

**New features available:**
```python
# NotifAI - AI-powered notifications
response = client.notifai('deployment finished, v2.1.3 is live')

# Configurable retries
client = Pincho(token='abc12345', max_retries=5)

# Debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## [1.0.0] - 2025-10-26

### Added
- Initial release of Pincho Python library
- Synchronous client (`Pincho`) with context manager support
- Asynchronous client (`AsyncPincho`) with asyncio support
- httpx-based HTTP client with HTTP/2 support
- Full type hints and py.typed marker for IDE support
- Custom exceptions for better error handling:
  - `PinchoError` - Base exception
  - `AuthenticationError` - Auth failures (401, 403)
  - `ValidationError` - Invalid parameters (400, 404)
- Comprehensive test suite (31 tests, 94% coverage)
- Support for all v1 API parameters:
  - `title` and `message` (required)
  - `type` for notification categorization
  - `tags` for flexible organization (up to 10 tags)
  - `image_url` for visual attachments
  - `action_url` for tap actions
- Python 3.8+ support
- GCP Cloud Build CI/CD configuration
- Comprehensive documentation:
  - README with quickstart guide
  - API reference
  - Error handling guide
  - Usage examples (basic, async, Flask)
- MIT License

### Dependencies
- httpx >= 0.24.0 (only runtime dependency)

[Unreleased]: https://github.com/Pincho-App/pincho-python/compare/v1.0.0...main
[1.0.0]: https://github.com/Pincho-App/pincho-python/releases/tag/v1.0.0
