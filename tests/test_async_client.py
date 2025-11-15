"""Tests for asynchronous WirePusher client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from wirepusher import AsyncWirePusher
from wirepusher.exceptions import (
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

    def test_init_missing_token_raises_error(self) -> None:
        """Test that missing token raises ValueError."""
        with pytest.raises(ValueError, match="Token is required"):
            AsyncWirePusher()

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

        # Verify request payload
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.headers["Content-Type"] == "application/json"

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
                }
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
                    "param": "title"
                }
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
                }
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
                }
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
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={
                "status": "error",
                "error": {
                    "type": "server_error",
                    "code": "internal_error",
                    "message": "Internal server error",
                }
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
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        async with AsyncWirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        """Test timeout error handling."""
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
