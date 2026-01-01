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

    # Phase 3: Parts APIs - Singapore Focus (HYBRID SYSTEM)
    # Google Custom Search API - Active (searches Lazada, Shopee, Carousell)
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CSE_ID: Optional[str] = None  # Custom Search Engine ID
    GOOGLE_CSE_RATE_LIMIT: int = 100  # Free tier: 100 queries/day

    # eBay API Credentials - Ready to activate (waiting for credentials)
    EBAY_APP_ID: Optional[str] = None
    EBAY_DEV_ID: Optional[str] = None
    EBAY_CERT_ID: Optional[str] = None
    EBAY_ENVIRONMENT: str = "PRODUCTION"  # or SANDBOX
    EBAY_MARKETPLACE: str = "EBAY_SG"  # Singapore marketplace

    # Lazada API Credentials
    LAZADA_APP_KEY: Optional[str] = None
    LAZADA_APP_SECRET: Optional[str] = None
    LAZADA_REGION: str = "SG"  # Singapore

    # Shopee API Credentials
    SHOPEE_PARTNER_ID: Optional[str] = None
    SHOPEE_PARTNER_KEY: Optional[str] = None
    SHOPEE_SHOP_ID: Optional[str] = None

    # Amazon PA-API Credentials (Optional)
    AMAZON_ACCESS_KEY: Optional[str] = None
    AMAZON_SECRET_KEY: Optional[str] = None
    AMAZON_ASSOCIATE_TAG: Optional[str] = None
    AMAZON_REGION: str = "sg"

    # API Rate Limits
    EBAY_RATE_LIMIT: int = 5000  # calls per day
    LAZADA_RATE_LIMIT: int = 10000  # calls per day
    SHOPEE_RATE_LIMIT: int = 10000  # calls per day

    # Parts Search Settings
    SEARCH_CACHE_TTL: int = 3600  # 1 hour
    PARTS_CACHE_TTL: int = 86400  # 24 hours
    DEFAULT_RESULTS_LIMIT: int = 20
    MIN_SEARCH_CONFIDENCE: float = 0.5
    SINGAPORE_PRIORITY: bool = True  # Prioritize Singapore sellers

    # HYBRID SYSTEM: Data Source Flags
    USE_SYNTHETIC_DATA: bool = True  # Set to False when real APIs are ready
    USE_GOOGLE_CSE: bool = True  # ✅ ACTIVE - Google Custom Search for real-time data
    USE_EBAY_API: bool = False  # Set to True when credentials are added

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
