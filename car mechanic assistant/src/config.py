"""
Configuration management for the Car Mechanic RAG Assistant
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

class Config:
    """Configuration class for RAG system"""

    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
    CHROMA_PERSIST_DIR = BASE_DIR / os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

    # Gemini Models
    EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    GENERATION_MODEL = os.getenv("GEMINI_GENERATION_MODEL", "gemini-3.1-flash-lite")

    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "3072"))

    # Vector Database
    COLLECTION_NAME = os.getenv("COLLECTION_NAME", "mechanic_knowledge_base")

    # Retrieval Settings
    TOP_K_DOCUMENTS = int(os.getenv("TOP_K_DOCUMENTS", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    MIN_RETRIEVAL_SIMILARITY = float(os.getenv("MIN_RETRIEVAL_SIMILARITY", "0.65"))

    # Generation Settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

    # Workshop Rules (always loaded)
    WORKSHOP_RULES_PATH = BASE_DIR / "workshop_policy.md"

    # Folder priorities (for re-ranking)
    FOLDER_PRIORITIES = {
        "10_troubleshooting_database": 10,  # Known issues = highest priority
        "09_workshop_rules": 9,              # Always relevant
        "02_diagnostic_procedures": 8,       # Symptom-based diagnostics
        "03_fault_codes": 7,                 # Code interpretation
        "04_repair_procedures": 6,           # Repair steps
        "01_vehicle_specs": 5,               # Specs
        "05_parts_catalog": 4,               # Parts info
        "06_diagnostic_software": 4,         # Software procedures
        "07_paint_codes": 3,                 # Paint info
        "08_pricing_valuation": 3,           # Pricing
    }

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set in environment variables")

        if not cls.KNOWLEDGE_BASE_DIR.exists():
            raise ValueError(f"Knowledge base directory not found: {cls.KNOWLEDGE_BASE_DIR}")

        return True
