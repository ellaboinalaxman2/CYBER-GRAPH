"""
Configuration management for Cyber-Graph Ingestion Service.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    and the .env file.
    """

    # ============================================================
    # APPLICATION
    # ============================================================

    app_name: str = "Cyber-Graph-Ingestion"

    app_version: str = "1.0.0"

    environment: str = "development"

    debug: bool = True

    log_level: str = "INFO"

    # ============================================================
    # API
    # ============================================================

    api_host: str = "0.0.0.0"

    api_port: int = 8001

    api_prefix: str = "/api/v1"

    # ============================================================
    # DATABASE ENGINE
    # ============================================================

    database_url: str = "http://localhost:8003"

    # ============================================================
    # REDIS
    # ============================================================

    redis_host: str = "localhost"

    redis_port: int = 6379

    redis_db: int = 0

    redis_password: Optional[str] = None

    # ============================================================
    # JWT
    # ============================================================

    jwt_secret_key: str = "change-me-in-production"

    # ============================================================
    # DIRECTORIES
    # ============================================================

    data_dir: str = "./data"

    sample_data_dir: str = "./data/samples"

    failed_events_dir: str = "./data/failed"

    # ============================================================
    # COLLECTORS
    # ============================================================

    syslog_port: int = 514

    windows_event_log: str = "Security"

    # ============================================================
    # PYDANTIC SETTINGS CONFIG
    # ============================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# ================================================================
# SINGLETON
# ================================================================

settings = Settings()