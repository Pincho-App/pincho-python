"""Pytest configuration and fixtures for Pincho library tests."""

import pytest


@pytest.fixture
def test_token() -> str:
    """Test Pincho API token."""
    return "abc12345"


@pytest.fixture
def test_base_url() -> str:
    """Test base URL."""
    return "https://pincho-gateway-1xatwfdc.uc.gateway.dev"
