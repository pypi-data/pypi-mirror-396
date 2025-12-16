"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def sample_metadata_dict() -> dict[str, str]:
    """Sample metadata dictionary for testing."""
    return {"key1": "value1", "key2": "value2"}
