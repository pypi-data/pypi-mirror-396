"""Configuration for Gemini Agent API Server."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from gemini_agent._version import __version__


class Settings(BaseSettings):
    """Server configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "Gemini Agent API"
    app_version: str = __version__
    debug: bool = False

    # Gemini CLI settings
    gemini_api_key: str = ""
    gemini_timeout: int = 300
    gemini_model: str = ""  # Empty = let Gemini CLI choose

    # Redis and Celery settings
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # Task timeout settings
    task_soft_time_limit: int = 300
    task_time_limit: int = 360


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
