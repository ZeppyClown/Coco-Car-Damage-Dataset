#!/usr/bin/env python
"""Database initialization script"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from sqlalchemy import create_engine, text


def init_database():
    """Initialize the database with schema"""
    print(f"Connecting to database: {settings.DATABASE_URL}")

    engine = create_engine(settings.DATABASE_URL)

    try:
        with engine.connect() as conn:
            print("Connection successful!")

            # Read and execute init SQL
            sql_file = os.path.join(os.path.dirname(__file__), 'init_postgres.sql')
            if os.path.exists(sql_file):
                with open(sql_file, 'r') as f:
                    sql = f.read()
                    # Execute each statement separately
                    for statement in sql.split(';'):
                        if statement.strip():
                            conn.execute(text(statement))
                            conn.commit()
                print("Database schema initialized successfully!")
            else:
                print(f"SQL file not found: {sql_file}")

    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    init_database()
