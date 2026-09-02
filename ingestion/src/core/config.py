"""Configuration management using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="Cyber-Graph-Ingestion", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8001, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # JWT
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    
    # Directories
    data_dir: str = Field(default="./data", alias="DATA_DIR")
    sample_data_dir: str = Field(default="./data/samples", alias="SAMPLE_DATA_DIR")
    failed_events_dir: str = Field(default="./data/failed", alias="FAILED_EVENTS_DIR")
    
    # Collectors
    syslog_port: int = Field(default=514, alias="SYSLOG_PORT")
    windows_event_log: str = Field(default="Security", alias="WINDOWS_EVENT_LOG")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
settings = Settings()