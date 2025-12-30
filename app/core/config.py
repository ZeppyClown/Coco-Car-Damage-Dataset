from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Automotive Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"

    # Database
    DATABASE_URL: str = "postgresql://automotive:automotive123@localhost:5432/automotive_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "automotive123"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_KEY: Optional[str] = None

    # ML Models
    INTENT_MODEL_PATH: str = "data/models/intent_classifier_v1"
    PARTS_MODEL_PATH: str = "data/models/parts_classifier_v1"
    PAINT_MODEL_PATH: str = "data/models/paint_matcher_v1"

    # External APIs
    VIN_DECODER_API_KEY: Optional[str] = None
    MARKET_DATA_API_KEY: Optional[str] = None
    ROCKAUTO_API_KEY: Optional[str] = None
    AUTOZONE_API_KEY: Optional[str] = None
    KBB_API_KEY: Optional[str] = None
    EDMUNDS_API_KEY: Optional[str] = None

    # Performance
    CACHE_TTL_SECONDS: int = 3600
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT_SECONDS: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
