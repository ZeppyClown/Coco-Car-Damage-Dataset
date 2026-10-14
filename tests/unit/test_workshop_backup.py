"""Backup download and restore round trip; all records are the app's made-up examples or fictional fixtures."""
from pathlib import Path
import zipfile

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.models import Base, WorkshopDocument
from app.services.workshop_backup import TABLES, restore_backup

API = "/api/v1/workshop"
COMPANY = {"name": "Fictional Motor Works", "address": "1 Fictional Street", "gst_registration_number": "M2-0000000-0", "phone": "6000 0000"}
PNG = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()


@pytest.fixture
def shop(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    return client


def counts(connection):
    return {table.name: connection.scalar(select(func.count()).select_from(table)) for table in TABLES}


def test_backup_restores_every_record_and_photo_into_an_empty_database(shop, test_db, tmp_path):
    shop.put(API + "/setup", json=COMPANY)
    shop.post(API + "/setup/example-jobs")
    shop.post(API + "/documents", data={"data_origin": "synthetic_demo"}, files={"file": ("sheet.png", PNG, "image/png")})
    response = shop.get(API + "/backup")
    assert response.status_code == 200 and response.headers["content-type"] == "application/zip"
    assert "workshop-backup-" in response.headers["content-disposition"]
    backup = tmp_path / "backup.zip"
    backup.write_bytes(response.content)
    assert "manifest.json" in zipfile.ZipFile(backup).namelist()
    original = counts(test_db.connection())
    assert original["workshop_jobs"] > 40 and original["workshop_invoices"] and original["workshop_documents"] == 1

    fresh = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(fresh)
    with fresh.begin() as connection:
        restore_backup(connection, backup)
    with fresh.connect() as connection:
        assert counts(connection) == original
        assert connection.scalar(select(WorkshopDocument.__table__.c.content)) == PNG
    # A second restore into the same database is refused, so nothing is doubled.
    with fresh.begin() as connection, pytest.raises(ValueError, match="already has workshop records"):
        restore_backup(connection, backup)


def test_only_the_owner_can_download_a_backup(shop):
    shop.post(API + "/users", json={"username": "fictional-staff", "password": "staff fictional 2026", "role": "staff"})
    shop.auth = ("fictional-staff", "staff fictional 2026")
    assert shop.get(API + "/backup").status_code == 403


def test_restore_refuses_other_files(tmp_path, test_db):
    other = tmp_path / "other.zip"
    with zipfile.ZipFile(other, "w") as archive:
        archive.writestr("manifest.json", '{"format": "something else"}')
    with pytest.raises(ValueError, match="not a workshop backup"):
        restore_backup(test_db.connection(), other)
