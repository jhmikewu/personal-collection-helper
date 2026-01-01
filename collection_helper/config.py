"""Configuration management using environment variables."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Emby Configuration
    emby_url: Optional[str] = None
    emby_api_key: Optional[str] = None

    # Booklore Configuration
    booklore_url: Optional[str] = None
    booklore_api_key: Optional[str] = None

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8090  # Changed from 8080 to avoid qBittorrent conflict

    # Logging
    log_level: str = "INFO"

    # Cache Configuration
    cache_ttl: int = 3600  # seconds


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
