"""Synthetic uploads only; byte identity, limits and failure cleanup matter."""
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from PIL import Image
import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.models import WorkshopDocument
from app.services import workshop


PREFIX = "/api/v1/workshop/documents"
PNG = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()


@pytest.fixture
def source_client(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path / "private")
    return client


def upload(client, data=PNG, filename="demo.png", media="image/png", origin="synthetic_demo"):
    return client.post(PREFIX, data={"data_origin": origin}, files={"file": (filename, data, media)})


def test_upload_preview_duplicate_and_untrusted_filename(source_client, test_db):
    created = upload(source_client, filename="../../outside.png")
    assert created.status_code == 201 and not created.json()["duplicate"]
    source_id = created.json()["id"]
    preview = source_client.get(f"{PREFIX}/{source_id}/preview")
    assert preview.status_code == 200 and preview.content == PNG
    assert preview.headers["cache-control"] == "no-store" and preview.headers["x-content-type-options"] == "nosniff"
    duplicate = upload(source_client)
    assert duplicate.status_code == 201 and duplicate.json()["duplicate"]
    assert duplicate.json()["id"] == source_id
    assert upload(source_client, origin="private_source").status_code == 422
    assert test_db.scalar(select(func.count()).select_from(WorkshopDocument)) == 1
    files = list(settings.WORKSHOP_STORAGE_DIR.iterdir())
    assert len(files) == 1 and files[0].name != "outside.png"
    assert files[0].read_bytes() == PNG


def test_jpeg_is_decoded_and_retained(source_client):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), "white").save(buffer, format="JPEG")
    data = buffer.getvalue()
    created = upload(source_client, data, "demo.jpeg", "image/jpeg")
    assert created.status_code == 201
    assert source_client.get(f"{PREFIX}/{created.json()['id']}/preview").content == data


def test_source_routes_are_disabled(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert upload(client).status_code == 404
    assert client.get(f"{PREFIX}/{uuid4()}/preview").status_code == 404


@pytest.mark.parametrize("format", ["GIF", "PNG"])
def test_unsupported_or_animated_source_rejected(source_client, format):
    buffer = BytesIO()
    Image.new("RGB", (20, 20), "white").save(buffer, format=format, save_all=True, append_images=[Image.new("RGB", (20, 20), "black")])
    assert upload(source_client, buffer.getvalue(), "demo.png", "image/png").status_code == 415


@pytest.mark.parametrize("data,filename,media,status", [
    (b"", "empty.png", "image/png", 413),
    (b"not an image", "fake.png", "image/png", 422),
    (PNG[:100], "truncated.png", "image/png", 422),
    (PNG, "fake.jpg", "image/png", 415),
    (PNG, "demo.png", "image/jpeg", 415),
    (PNG, "demo.pdf", "application/pdf", 415),
])
def test_bad_upload_has_no_row_or_file(source_client, test_db, data, filename, media, status):
    assert upload(source_client, data, filename, media).status_code == status
    assert test_db.scalar(select(func.count()).select_from(WorkshopDocument)) == 0
    assert not settings.WORKSHOP_STORAGE_DIR.exists()


def test_size_dimension_pixel_and_streamed_request_limits(source_client, monkeypatch):
    assert upload(source_client, b"x" * (workshop.MAX_UPLOAD_BYTES + 1)).status_code == 413
    buffer = BytesIO()
    Image.new("RGB", (6001, 1)).save(buffer, format="PNG")
    assert upload(source_client, buffer.getvalue()).status_code == 413
    with monkeypatch.context() as patch:
        patch.setattr(workshop, "MAX_IMAGE_PIXELS", 10)
        assert upload(source_client).status_code == 413
    chunks = (chunk for chunk in [b"--boundary\r\n", b"x" * (workshop.MAX_UPLOAD_BYTES + 65537)])
    response = source_client.post(PREFIX, content=chunks, headers={"Content-Type": "multipart/form-data; boundary=boundary"})
    assert response.status_code == 413
    assert response.headers["x-request-id"]


def test_unknown_missing_corrupt_and_unsafe_stored_path(source_client, test_db):
    assert source_client.get(f"{PREFIX}/{uuid4()}/preview").status_code == 404
    created = upload(source_client).json()
    document = test_db.scalar(select(WorkshopDocument))
    path = settings.WORKSHOP_STORAGE_DIR / document.storage_key
    path.write_bytes(b"changed")
    assert source_client.get(f"{PREFIX}/{created['id']}/preview").status_code == 503
    assert upload(source_client).status_code == 503
    path.unlink()
    assert source_client.get(f"{PREFIX}/{created['id']}/preview").status_code == 503
    document.storage_key = "../../outside.png"
    test_db.commit()
    assert source_client.get(f"{PREFIX}/{created['id']}/preview").status_code == 503


def test_database_failure_removes_new_file(source_client, test_db, monkeypatch):
    def fail_commit():
        raise OperationalError("fixture", {}, RuntimeError("PRIVATE TEST VALUE"))
    with monkeypatch.context() as patch:
        patch.setattr(test_db, "commit", fail_commit)
        result = upload(source_client)
    assert result.status_code == 500 and "PRIVATE TEST VALUE" not in result.text
    assert list(settings.WORKSHOP_STORAGE_DIR.iterdir()) == []
    assert test_db.scalar(select(func.count()).select_from(WorkshopDocument)) == 0


def test_storage_failure_and_static_directory_rejected(source_client, test_db, monkeypatch, tmp_path):
    blocker = tmp_path / "not-a-directory"
    blocker.write_text("fictional blocker")
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", blocker)
    assert upload(source_client).status_code == 503
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", Path("app/static/private"))
    assert upload(source_client).status_code == 503
    assert test_db.scalar(select(func.count()).select_from(WorkshopDocument)) == 0
