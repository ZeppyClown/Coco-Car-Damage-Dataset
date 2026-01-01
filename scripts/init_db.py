#!/usr/bin/env python
"""Database initialization script"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.db.models import Base
from sqlalchemy import create_engine


def init_database():
    """Initialize the database with schema using SQLAlchemy models"""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_engine(settings.DATABASE_URL)

    try:
        print("Connection successful!")

        # Create all tables from SQLAlchemy models
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)

        print("✓ Database schema initialized successfully!")
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    init_database()
