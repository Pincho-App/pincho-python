"""Tests for asynchronous WirePusher client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from wirepusher_official import AsyncWirePusher
from wirepusher_official.exceptions import (
    AuthenticationError,
    ValidationError,
    WirePusherError,
)


class TestAsyncWirePusher:
    """Test suite for AsyncWirePusher asynchronous client."""

    def test_init(self) -> None:
        """Test client initialization with token."""
        client = AsyncWirePusher(token="abc12345")
        assert client.token == "abc12345"
        assert client.timeout == 30.0
        assert client.base_url == AsyncWirePusher.BASE_URL

    def test_init_missing_token_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that missing token raises ValueError."""
        # Ensure no env var is set
        monkeypatch.delenv("WIREPUSHER_TOKEN", raising=False)
        with pytest.raises(ValueError, match="Token is required"):
            AsyncWirePusher()

    def test_init_empty_token_raises_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that empty token raises ValueError."""
        monkeypatch.delenv("WIREPUSHER_TOKEN", raising=False)
        with pytest.raises(ValueError, match="Token is required"):
            AsyncWirePusher(token="")

    def test_init_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test client initialization from WIREPUSHER_TOKEN env var."""
        monkeypatch.setenv("WIREPUSHER_TOKEN", "env_token_123")
        client = AsyncWirePusher()
        assert client.token == "env_token_123"

    def test_init_timeout_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test timeout initialization from WIREPUSHER_TIMEOUT env var."""
        monkeypatch.setenv("WIREPUSHER_TIMEOUT", "60.0")
        client = AsyncWirePusher(token="abc12345")
        assert client.timeout == 60.0

    def test_init_max_retries_from_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test max_retries initialization from WIREPUSHER_MAX_RETRIES env var."""
        monkeypatch.setenv("WIREPUSHER_MAX_RETRIES", "5")
        client = AsyncWirePusher(token="abc12345")
        assert client.max_retries == 5

    def test_init_explicit_overrides_env_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that explicit parameters override environment variables."""
        monkeypatch.setenv("WIREPUSHER_TOKEN", "env_token")
        monkeypatch.setenv("WIREPUSHER_TIMEOUT", "60.0")
        monkeypatch.setenv("WIREPUSHER_MAX_RETRIES", "5")
        client = AsyncWirePusher(token="explicit_token", timeout=10.0, max_retries=1)
        assert client.token == "explicit_token"
        assert client.timeout == 10.0
        assert client.max_retries == 1

    def test_init_custom_timeout(self) -> None:
        """Test client initialization with custom timeout."""
        client = AsyncWirePusher(token="abc12345", timeout=60.0)
        assert client.timeout == 60.0

    def test_init_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = AsyncWirePusher(
            token="abc12345",
            base_url="https://custom.example.com",
        )
        assert client.base_url == "https://custom.example.com"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test client as async context manager."""
        async with AsyncWirePusher(token="abc12345") as client:
            assert client.token == "abc12345"
        # Client should be closed after exiting context

    @pytest.mark.asyncio
    async def test_send_success(self, httpx_mock: HTTPXMock) -> None:
        """Test successful notification send."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={"status": "success", "message": "Notification sent successfully"},
            status_code=200,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            response = await client.send("Test Title", "Test message")
            assert response.status == "success"
            assert response.message == "Notification sent successfully"

    @pytest.mark.asyncio
    async def test_send_with_all_parameters(self, httpx_mock: HTTPXMock) -> None:
        """Test send with all optional parameters."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={"status": "success", "message": "Notification sent"},
            status_code=200,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            response = await client.send(
                "Test Title",
                "Test message",
                type="alert",
                tags=["urgent", "production"],
                image_url="https://example.com/image.png",
                action_url="https://example.com/action",
            )
            assert response.status == "success"

        # Verify request payload and headers
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["Authorization"] == "Bearer abc12345"

        # Verify token is NOT in request body
        import json

        body = json.loads(request.content.decode())
        assert "token" not in body

    @pytest.mark.asyncio
    async def test_send_authentication_error_401(self, httpx_mock: HTTPXMock) -> None:
        """Test 401 authentication error with nested error format."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={
                "status": "error",
                "error": {
                    "type": "authentication_error",
                    "code": "invalid_token",
                    "message": "Invalid token",
                },
            },
            status_code=401,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Invalid token" in str(exc_info.value)
            assert "[invalid_token]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_validation_error_400(self, httpx_mock: HTTPXMock) -> None:
        """Test 400 validation error with nested error format."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={
                "status": "error",
                "error": {
                    "type": "validation_error",
                    "code": "missing_required_field",
                    "message": "Title is required",
                    "param": "title",
                },
            },
            status_code=400,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.send("", "Test message")
            assert "Invalid parameters" in str(exc_info.value)
            assert "Title is required" in str(exc_info.value)
            assert "(parameter: title)" in str(exc_info.value)
            assert "[missing_required_field]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_forbidden_error_403(self, httpx_mock: HTTPXMock) -> None:
        """Test 403 forbidden error with nested error format."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={
                "status": "error",
                "error": {
                    "type": "authentication_error",
                    "code": "account_disabled",
                    "message": "Account disabled",
                },
            },
            status_code=403,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Forbidden" in str(exc_info.value)
            assert "[account_disabled]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_not_found_error_404(self, httpx_mock: HTTPXMock) -> None:
        """Test 404 not found error with nested error format."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={
                "status": "error",
                "error": {
                    "type": "validation_error",
                    "code": "not_found",
                    "message": "User not found",
                },
            },
            status_code=404,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "User not found" in str(exc_info.value)
            assert "[not_found]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_server_error_500(self, httpx_mock: HTTPXMock) -> None:
        """Test 500 server error with nested error format."""
        # Server error is retryable, so mock will be called 4 times (initial + 3 retries)
        for _ in range(4):
            httpx_mock.add_response(
                method="POST",
                url="https://api.wirepusher.dev/send",
                json={
                    "status": "error",
                    "error": {
                        "type": "server_error",
                        "code": "internal_error",
                        "message": "Internal server error",
                    },
                },
                status_code=500,
            )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Server error (500)" in str(exc_info.value)
            assert "[internal_error]" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_network_error(self, httpx_mock: HTTPXMock) -> None:
        """Test network error handling."""
        # Network error is retryable, so mock will be called 4 times (initial + 3 retries)
        for _ in range(4):
            httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        """Test timeout error handling."""
        # Timeout is retryable, so mock will be called 4 times (initial + 3 retries)
        for _ in range(4):
            httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        async with AsyncWirePusher(token="abc12345", timeout=1.0) as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_malformed_json_response(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of malformed JSON response."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            content=b"not json",
            status_code=200,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_missing_response_fields(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of response with missing fields."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={},
            status_code=200,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            response = await client.send("Test Title", "Test message")
            assert response.status == "unknown"
            assert response.message == ""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_sends(self, httpx_mock: HTTPXMock) -> None:
        """Test multiple concurrent sends (async benefit)."""
        import asyncio

        # Mock response for all requests (add multiple times for concurrent sends)
        for _ in range(3):
            httpx_mock.add_response(
                method="POST",
                url="https://api.wirepusher.dev/send",
                json={"status": "success", "message": "Notification sent"},
                status_code=200,
            )

        async with AsyncWirePusher(token="abc12345") as client:
            # Send 3 notifications concurrently
            tasks = [client.send(f"Title {i}", f"Message {i}") for i in range(3)]
            responses = await asyncio.gather(*tasks)

            # All should succeed
            assert len(responses) == 3
            for response in responses:
                assert response.status == "success"

    @pytest.mark.asyncio
    async def test_notifai_success(self, httpx_mock: HTTPXMock) -> None:
        """Test successful NotifAI notification generation."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/notifai",
            json={
                "status": "success",
                "message": "Notification generated and sent successfully",
                "notification": {
                    "title": "Deploy Complete - v2.1.3",
                    "message": "Your deployment to production has finished successfully",
                    "type": "deployment",
                    "tags": ["production", "deploy"],
                },
            },
            status_code=200,
        )

        async with AsyncWirePusher(token="abc12345") as client:
            response = await client.notifai(
                "deployment finished successfully, v2.1.3 is live on prod"
            )
            assert response.status == "success"
            assert response.notification is not None
            assert "title" in response.notification

        # Verify Authorization header is sent
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.headers["Authorization"] == "Bearer abc12345"

        # Verify token is NOT in request body
        import json

        body = json.loads(request.content.decode())
        assert "token" not in body
