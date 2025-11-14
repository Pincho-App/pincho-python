"""Pytest configuration and fixtures for WirePusher library tests."""

import pytest


@pytest.fixture
def test_token() -> str:
    """Test WirePusher API token."""
    return "abc12345"


@pytest.fixture
def test_base_url() -> str:
    """Test base URL."""
    return "https://wirepusher-gateway-1xatwfdc.uc.gateway.dev"
