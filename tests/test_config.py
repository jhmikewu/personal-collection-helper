"""Tests for configuration management."""

import pytest
from collection_helper.config import Settings, get_settings


def test_settings_default_values():
    """Test that settings have proper default values."""
    settings = Settings(
        emby_url="http://localhost:8096",
        emby_api_key="test_key",
        booklore_url="http://localhost:8080",
    )

    assert settings.host == "0.0.0.0"
    assert settings.port == 8080
    assert settings.log_level == "INFO"
    assert settings.cache_ttl == 3600


def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2
