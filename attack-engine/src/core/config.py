"""Configuration management for Member 5 - Attack Engine."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="Cyber-Graph-Attack-Engine", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8004, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # Member URLs
    member2_url: str = Field(default="http://localhost:8001", alias="MEMBER2_URL")
    member3_url: str = Field(default="http://localhost:8002", alias="MEMBER3_URL")
    member4_url: str = Field(default="http://localhost:8003", alias="MEMBER4_URL")
    
    # Risk Settings
    risk_low_threshold: int = Field(default=20, alias="RISK_LOW_THRESHOLD")
    risk_medium_threshold: int = Field(default=40, alias="RISK_MEDIUM_THRESHOLD")
    risk_high_threshold: int = Field(default=70, alias="RISK_HIGH_THRESHOLD")
    risk_critical_threshold: int = Field(default=85, alias="RISK_CRITICAL_THRESHOLD")
    
    # MITRE Settings
    mitre_data_path: str = Field(default="./data/mitre/attack_techniques.json", alias="MITRE_DATA_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


settings = Settings()