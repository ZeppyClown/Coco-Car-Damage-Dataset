"""A whole-workshop backup the owner can download, and putting it back into an empty database.

The file is a zip: manifest.json plus one JSON-lines file per workshop table, photos included (base64). It needs no
PostgreSQL tools, so it works the same from the hosted app and on a laptop, and moves the books to a new database."""
import base64
import json
import zipfile
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, inspect, select, text
from sqlalchemy.engine import Connection

from app.db.models import Base

FORMAT = "yap-workshop-backup-1"
TABLES = [table for table in Base.metadata.sorted_tables if table.name.startswith("workshop_")]  # parents first


def _version(connection: Connection) -> str | None:
    if not inspect(connection).has_table("alembic_version"):
        return None
    return connection.scalar(text("SELECT version_num FROM alembic_version"))


def _out(value):
    if isinstance(value, bytes):
        return base64.b64encode(value).decode()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    return value


def _in(column, value):
    if value is None:
        return None
    try:
        kind = column.type.python_type
    except NotImplementedError:
        return value
    if kind is bytes:
        return base64.b64decode(value)
    if kind is datetime:
        moment = datetime.fromisoformat(value)
        return moment if moment.tzinfo or not getattr(column.type, "timezone", False) else moment.replace(tzinfo=timezone.utc)
    if kind is date:
        return date.fromisoformat(value)
    if kind in (Decimal, UUID):
        return kind(value)
    return value


def write_backup(connection: Connection, path) -> dict:
    """Write every workshop table to a zip at path, one row at a time so photos never all sit in memory."""
    counts = {}
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for table in TABLES:
            counts[table.name] = 0
            with archive.open(table.name + ".jsonl", "w") as output:
                rows = connection.execution_options(stream_results=True, yield_per=50).execute(select(table))
                for row in rows.mappings():
                    output.write((json.dumps({name: _out(value) for name, value in row.items()}) + "\n").encode())
                    counts[table.name] += 1
        manifest = {"format": FORMAT, "database_version": _version(connection), "made_at": datetime.now(timezone.utc).isoformat(), "rows": counts}
        archive.writestr("manifest.json", json.dumps(manifest, indent=1))
    return manifest


def restore_backup(connection: Connection, path) -> dict:
    """Load a backup into a database that is at the same version and has no workshop rows yet. The caller commits."""
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("format") != FORMAT:
            raise ValueError("This is not a workshop backup file")
        if manifest["database_version"] != _version(connection):
            raise ValueError(f"The backup is from database version {manifest['database_version']}, this database is at "
                             f"{_version(connection)}. Start the app once against it so it updates, then try again.")
        filled = [table.name for table in TABLES if connection.scalar(select(func.count()).select_from(table))]
        if filled:
            raise ValueError("The database already has workshop records in: " + ", ".join(filled))
        for table in TABLES:
            with archive.open(table.name + ".jsonl") as lines:
                batch = []
                for line in lines:
                    row = json.loads(line)
                    batch.append({name: _in(table.c[name], value) for name, value in row.items()})
                    if len(batch) == 50:
                        connection.execute(table.insert(), batch)
                        batch = []
                if batch:
                    connection.execute(table.insert(), batch)
    return manifest
