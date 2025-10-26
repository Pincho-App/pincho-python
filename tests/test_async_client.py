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
        """Test client initialization."""
        client = AsyncWirePusher(token="wpt_test123", user_id="user123")
        assert client.token == "wpt_test123"
        assert client.user_id == "user123"
        assert client.timeout == 30.0
        assert client.base_url == AsyncWirePusher.BASE_URL

    def test_init_custom_timeout(self) -> None:
        """Test client initialization with custom timeout."""
        client = AsyncWirePusher(token="wpt_test123", user_id="user123", timeout=60.0)
        assert client.timeout == 60.0

    def test_init_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = AsyncWirePusher(
            token="wpt_test123",
            user_id="user123",
            base_url="https://custom.example.com",
        )
        assert client.base_url == "https://custom.example.com"

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test client as async context manager."""
        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            assert client.token == "wpt_test123"
        # Client should be closed after exiting context

    @pytest.mark.asyncio
    async def test_send_success(self, httpx_mock: HTTPXMock) -> None:
        """Test successful notification send."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "success", "message": "Notification sent successfully"},
            status_code=200,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            response = await client.send("Test Title", "Test message")
            assert response.status == "success"
            assert response.message == "Notification sent successfully"

    @pytest.mark.asyncio
    async def test_send_with_all_parameters(self, httpx_mock: HTTPXMock) -> None:
        """Test send with all optional parameters."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "success", "message": "Notification sent"},
            status_code=200,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
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
        """Test 401 authentication error."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "error", "message": "Invalid token"},
            status_code=401,
        )

        async with AsyncWirePusher(token="invalid_token", user_id="user123") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Invalid token or user ID" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_validation_error_400(self, httpx_mock: HTTPXMock) -> None:
        """Test 400 validation error."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "error", "message": "Title is required"},
            status_code=400,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.send("", "Test message")
            assert "Invalid parameters" in str(exc_info.value)
            assert "Title is required" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_forbidden_error_403(self, httpx_mock: HTTPXMock) -> None:
        """Test 403 forbidden error."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "error", "message": "Account disabled"},
            status_code=403,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Forbidden" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_not_found_error_404(self, httpx_mock: HTTPXMock) -> None:
        """Test 404 not found error."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "error", "message": "User not found"},
            status_code=404,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="invalid_user") as client:
            with pytest.raises(ValidationError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "User not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_server_error_500(self, httpx_mock: HTTPXMock) -> None:
        """Test 500 server error."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={"status": "error", "message": "Internal server error"},
            status_code=500,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "API error (500)" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_network_error(self, httpx_mock: HTTPXMock) -> None:
        """Test network error handling."""
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        """Test timeout error handling."""
        httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        async with AsyncWirePusher(token="wpt_test123", user_id="user123", timeout=1.0) as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_malformed_json_response(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of malformed JSON response."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            content=b"not json",
            status_code=200,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            with pytest.raises(WirePusherError) as exc_info:
                await client.send("Test Title", "Test message")
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_missing_response_fields(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of response with missing fields."""
        httpx_mock.add_response(
            method="POST",
            url="https://wirepusher.com/send",
            json={},
            status_code=200,
        )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
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
                url="https://wirepusher.com/send",
                json={"status": "success", "message": "Notification sent"},
                status_code=200,
            )

        async with AsyncWirePusher(token="wpt_test123", user_id="user123") as client:
            # Send 3 notifications concurrently
            tasks = [client.send(f"Title {i}", f"Message {i}") for i in range(3)]
            responses = await asyncio.gather(*tasks)

            # All should succeed
            assert len(responses) == 3
            for response in responses:
                assert response.status == "success"
