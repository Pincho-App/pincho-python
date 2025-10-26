"""Pytest configuration and fixtures for WirePusher SDK tests."""

import pytest


@pytest.fixture
def test_token() -> str:
    """Test WirePusher API token."""
    return "wpt_test123"


@pytest.fixture
def test_user_id() -> str:
    """Test user ID."""
    return "user123"


@pytest.fixture
def test_base_url() -> str:
    """Test base URL."""
    return "https://wirepusher-gateway-1xatwfdc.uc.gateway.dev"
