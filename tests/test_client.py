"""Tests for synchronous WirePusher client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from wirepusher_official import WirePusher
from wirepusher_official.exceptions import (
    AuthenticationError,
    ValidationError,
    WirePusherError,
)


class TestWirePusher:
    """Test suite for WirePusher synchronous client."""

    def test_init(self) -> None:
        """Test client initialization with token."""
        client = WirePusher(token="abc12345")
        assert client._async_client.token == "abc12345"
        assert client._async_client.timeout == 30.0
        assert client._async_client.base_url == "https://api.wirepusher.dev"
        client.close()

    def test_init_missing_token_raises_error(self) -> None:
        """Test that missing token raises ValueError."""
        with pytest.raises(ValueError, match="Token is required"):
            WirePusher(token="")

    def test_init_custom_timeout(self) -> None:
        """Test client initialization with custom timeout."""
        client = WirePusher(token="abc12345", timeout=60.0)
        assert client._async_client.timeout == 60.0
        client.close()

    def test_init_custom_base_url(self) -> None:
        """Test client initialization with custom base URL."""
        client = WirePusher(
            token="abc12345",
            base_url="https://custom.example.com",
        )
        assert client._async_client.base_url == "https://custom.example.com"
        client.close()

    def test_context_manager(self) -> None:
        """Test client as context manager."""
        with WirePusher(token="abc12345") as client:
            assert client._async_client.token == "abc12345"
        # Client should be closed after exiting context

    def test_send_success(self, httpx_mock: HTTPXMock) -> None:
        """Test successful notification send."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={"status": "success", "message": "Notification sent successfully"},
            status_code=200,
        )

        with WirePusher(token="abc12345") as client:
            response = client.send("Test Title", "Test message")
            assert response.status == "success"
            assert response.message == "Notification sent successfully"

    def test_send_with_all_parameters(self, httpx_mock: HTTPXMock) -> None:
        """Test send with all optional parameters."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={"status": "success", "message": "Notification sent"},
            status_code=200,
        )

        with WirePusher(token="abc12345") as client:
            response = client.send(
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

    def test_send_authentication_error_401(self, httpx_mock: HTTPXMock) -> None:
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

        with WirePusher(token="abc12345") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Invalid token" in str(exc_info.value)
            assert "[invalid_token]" in str(exc_info.value)

    def test_send_validation_error_400(self, httpx_mock: HTTPXMock) -> None:
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

        with WirePusher(token="abc12345") as client:
            with pytest.raises(ValidationError) as exc_info:
                client.send("", "Test message")
            assert "Invalid parameters" in str(exc_info.value)
            assert "Title is required" in str(exc_info.value)
            assert "(parameter: title)" in str(exc_info.value)
            assert "[missing_required_field]" in str(exc_info.value)

    def test_send_forbidden_error_403(self, httpx_mock: HTTPXMock) -> None:
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

        with WirePusher(token="abc12345") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Forbidden" in str(exc_info.value)
            assert "[account_disabled]" in str(exc_info.value)

    def test_send_not_found_error_404(self, httpx_mock: HTTPXMock) -> None:
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

        with WirePusher(token="abc12345") as client:
            with pytest.raises(ValidationError) as exc_info:
                client.send("Test Title", "Test message")
            assert "User not found" in str(exc_info.value)
            assert "[not_found]" in str(exc_info.value)

    def test_send_server_error_500(self, httpx_mock: HTTPXMock) -> None:
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

        with WirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Server error (500)" in str(exc_info.value)
            assert "[internal_error]" in str(exc_info.value)

    def test_send_network_error(self, httpx_mock: HTTPXMock) -> None:
        """Test network error handling."""
        # Network error is retryable, so mock will be called 4 times (initial + 3 retries)
        for _ in range(4):
            httpx_mock.add_exception(httpx.ConnectError("Connection failed"))

        with WirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    def test_send_timeout_error(self, httpx_mock: HTTPXMock) -> None:
        """Test timeout error handling."""
        # Timeout is retryable, so mock will be called 4 times (initial + 3 retries)
        for _ in range(4):
            httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        with WirePusher(token="abc12345", timeout=1.0) as client:
            with pytest.raises(WirePusherError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Network error" in str(exc_info.value)

    def test_send_malformed_json_response(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of malformed JSON response."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            content=b"not json",
            status_code=200,
        )

        with WirePusher(token="abc12345") as client:
            with pytest.raises(WirePusherError) as exc_info:
                client.send("Test Title", "Test message")
            assert "Unexpected error" in str(exc_info.value)

    def test_send_missing_response_fields(self, httpx_mock: HTTPXMock) -> None:
        """Test handling of response with missing fields."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.wirepusher.dev/send",
            json={},
            status_code=200,
        )

        with WirePusher(token="abc12345") as client:
            response = client.send("Test Title", "Test message")
            assert response.status == "unknown"
            assert response.message == ""
