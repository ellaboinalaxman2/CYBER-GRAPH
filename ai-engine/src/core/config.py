"""Configuration management for Member 3 - AI Engine."""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # ========================================================================
    # Application Settings
    # ========================================================================
    app_name: str = Field(default="Cyber-Graph-AI-Engine", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # ========================================================================
    # API Settings
    # ========================================================================
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8002, alias="API_PORT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    
    # ========================================================================
    # ML Settings
    # ========================================================================
    random_seed: int = Field(default=42, alias="RANDOM_SEED")
    model_save_dir: str = Field(default="./data/models", alias="MODEL_SAVE_DIR")
    checkpoint_dir: str = Field(default="./data/models/checkpoints", alias="CHECKPOINT_DIR")
    
    # ========================================================================
    # Data Paths
    # ========================================================================
    raw_data_dir: str = Field(default="./data/raw", alias="RAW_DATA_DIR")
    processed_data_dir: str = Field(default="./data/processed", alias="PROCESSED_DATA_DIR")
    feature_dir: str = Field(default="./data/features", alias="FEATURE_DIR")
    
    # ========================================================================
    # Neo4j (Member 4)
    # ========================================================================
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    
    # ========================================================================
    # MongoDB (Member 4)
    # ========================================================================
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGODB_URI")
    mongodb_db: str = Field(default="cyber_graph", alias="MONGODB_DB")
    
    # ========================================================================
    # Integrations
    # ========================================================================
    ingestion_api_url: str = Field(default="http://localhost:8001/api/v1", alias="INGESTION_API_URL")
    attack_engine_url: str = Field(default="http://localhost:8003/api/v1", alias="ATTACK_ENGINE_URL")
    
    # ========================================================================
    # Model Architecture
    # ========================================================================
    model_name: str = Field(default="GraphSAGE", alias="MODEL_NAME")
    model_version: str = Field(default="1.0.0", alias="MODEL_VERSION")
    hidden_channels: int = Field(default=128, alias="HIDDEN_CHANNELS")
    num_layers: int = Field(default=3, alias="NUM_LAYERS")
    dropout: float = Field(default=0.2, alias="DROPOUT")
    
    # ========================================================================
    # Training Settings
    # ========================================================================
    learning_rate: float = Field(default=0.001, alias="LEARNING_RATE")
    weight_decay: float = Field(default=5e-4, alias="WEIGHT_DECAY")
    max_epochs: int = Field(default=200, alias="MAX_EPOCHS")
    batch_size: int = Field(default=1024, alias="BATCH_SIZE")
    patience: int = Field(default=20, alias="PATIENCE")
    
    # ========================================================================
    # Data Splits
    # ========================================================================
    train_split: float = Field(default=0.7, alias="TRAIN_SPLIT")
    val_split: float = Field(default=0.15, alias="VAL_SPLIT")
    test_split: float = Field(default=0.15, alias="TEST_SPLIT")
    
    # ========================================================================
    # GPU Settings
    # ========================================================================
    use_gpu: bool = Field(default=True, alias="USE_GPU")
    gpu_device: int = Field(default=0, alias="GPU_DEVICE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton instance
settings = Settings()