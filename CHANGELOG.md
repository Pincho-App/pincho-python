# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-26

### Added
- Initial release of WirePusher Python SDK
- Synchronous client (`WirePusher`) with context manager support
- Asynchronous client (`AsyncWirePusher`) with asyncio support
- httpx-based HTTP client with HTTP/2 support
- Full type hints and py.typed marker for IDE support
- Custom exceptions for better error handling:
  - `WirePusherError` - Base exception
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

[Unreleased]: https://gitlab.com/wirepusher/python-sdk/-/compare/v1.0.0...main
[1.0.0]: https://gitlab.com/wirepusher/python-sdk/-/tags/v1.0.0
