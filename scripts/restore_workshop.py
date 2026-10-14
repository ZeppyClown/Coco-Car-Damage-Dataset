"""Put a workshop backup (the zip from Workshop details > Download backup) into an empty database.

Usage: DATABASE_URL=postgresql://... python scripts/restore_workshop.py workshop-backup-....zip
Start the app against the new database once first, so its tables exist and are at the same version as the backup.
Nothing is written unless every table loads."""
import sys

from sqlalchemy import create_engine

from app.core.config import settings
from app.services.workshop_backup import restore_backup


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.begin() as connection:
            manifest = restore_backup(connection, sys.argv[1])
    except ValueError as error:
        raise SystemExit(f"Not restored: {error}") from None
    print("Restored:", ", ".join(f"{name} {count}" for name, count in manifest["rows"].items() if count) or "an empty backup")


if __name__ == "__main__":
    main()
