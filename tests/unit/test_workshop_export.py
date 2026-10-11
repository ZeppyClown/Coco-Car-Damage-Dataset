"""Deterministic demo mapping, safe cells and failure-safe private outputs."""
from copy import deepcopy
import csv
from datetime import datetime, timezone
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.models import WorkshopExport
from app.schemas.workshop import WorkshopRevisionResponse
from app.services.workshop import demo_csv


EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
API = "/api/v1/workshop"


def rows(content):
    return list(csv.DictReader(StringIO(content.decode("utf-8-sig"), newline="")))


def revision(record=None):
    return WorkshopRevisionResponse(
        id=UUID(int=1), job_id=UUID(int=2), version=3, record=record or EXAMPLE,
        reviewer="Fictional reviewer", reviewed_at=datetime(2026, 10, 11, tzinfo=timezone.utc),
    )


def test_exact_demo_row_and_reproducibility():
    snapshot = revision()
    content = demo_csv(snapshot)
    assert content.startswith(b"\xef\xbb\xbf")
    assert rows(content) == [{
        "mapping_version": "workshop-demo-v1", "output_kind": "DEMO_ONLY",
        "job_id": str(UUID(int=2)), "revision_id": str(UUID(int=1)), "revision": "3",
        "data_origin": "synthetic_demo", "record_stage": "quote", "job_reference": "DEMO-JOB-001",
        "customer_reference": "Fictional Example Person", "vehicle_reference": "DEMO-VEHICLE-A",
        "make": "", "model": "", "currency": "SGD", "line_number": "1", "cancelled": "false",
        "description": "Example filter replacement", "amount": "25.10",
        "description_raw": "Example filter replacement", "amount_raw": "25.10",
        "diagram_notes": "", "diagram_notes_raw": "", "written_total": "", "written_adjustment": "",
        "written_grand_total": "", "date_note_raw": "", "quotation_date": "", "date_in": "", "date_out": "",
        "reviewer": "Fictional reviewer", "reviewed_at": "2026-10-11T00:00:00+00:00",
        "source_document_id": "", "manual_provenance": "Authored fictional example, not a company document.",
    }]
    assert demo_csv(snapshot) == content


@pytest.mark.parametrize("text", ["=1+1", "+1+1", "-1+1", "@SUM(A1)", "  =1", "\ttext", "\rtext", "\ntext", "＝1+1"])
def test_formula_like_text_is_escaped_but_record_unchanged(text):
    record = deepcopy(EXAMPLE)
    record["diagram_notes_raw"] = text
    snapshot = revision(record)
    assert rows(demo_csv(snapshot))[0]["diagram_notes_raw"] == "'" + text
    assert snapshot.record.diagram_notes_raw == text


def test_unicode_newlines_null_zero_and_cancelled_raw_survive():
    record = deepcopy(EXAMPLE)
    record["items"] = [
        {"description": '示例, "door"\ninspection', "description_state": "confirmed", "description_raw": "literal\n示例"},
        {"description": "Zero", "description_state": "confirmed", "amount": "0.00", "amount_state": "confirmed"},
        {"description_raw": "Crossed out / 划掉", "amount_raw": "80 cancelled", "description": "Unreviewed meaning",
         "description_state": "proposed", "amount": "80.00", "amount_state": "proposed", "cancelled": True},
    ]
    record["written_adjustment"] = "-2.50"
    record["field_states"]["written_adjustment"] = "confirmed"
    output = rows(demo_csv(revision(record)))
    assert output[0]["description"] == '示例, "door"\ninspection' and output[0]["description_raw"] == "literal\n示例"
    assert [row["amount"] for row in output] == ["", "0.00", ""]
    assert output[2]["cancelled"] == "true" and output[2]["description"] == "" and output[2]["amount_raw"] == "80 cancelled"
    assert output[0]["written_adjustment"] == "'-2.50"


@pytest.fixture
def export_client(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    return client


def confirmed(client, record=None):
    job = client.post(API + "/jobs", json=record or EXAMPLE).json()
    result = client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 1, "reviewer": "Fictional reviewer", "acknowledged": True,
    })
    assert result.status_code == 200
    return job, result.json()


def test_export_repeat_download_correction_and_draft_gate(export_client, test_db):
    job, snapshot = confirmed(export_client)
    assert export_client.post(API + f"/revisions/{job['id']}/exports").status_code == 404
    path = API + f"/revisions/{snapshot['id']}/exports"
    first = export_client.post(path)
    assert first.status_code == 200
    exported = first.json()
    assert exported["status"] == "generated" and exported["created_at"].endswith("Z")
    assert export_client.post(path).json() == exported
    download = export_client.get(API + f"/exports/{exported['id']}/download")
    assert download.status_code == 200 and download.headers["cache-control"] == "no-store"
    assert 'attachment;' in download.headers["content-disposition"]
    assert sha256(download.content).hexdigest() == exported["checksum"]
    assert len(download.content) == exported["byte_size"]
    stored = test_db.get(WorkshopExport, UUID(exported["id"]))
    assert os.stat(settings.WORKSHOP_STORAGE_DIR / stored.storage_key).st_mode & 0o777 == 0o600
    corrected = {**job["draft"], "job_reference": "DEMO-CORRECTED"}
    export_client.patch(API + f"/jobs/{job['id']}", json={"expected_version": 1, "draft": corrected})
    second = export_client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 2, "reviewer": "Fictional", "acknowledged": True,
    }).json()
    other = export_client.post(API + f"/revisions/{second['id']}/exports").json()
    assert other["id"] != exported["id"] and other["checksum"] != exported["checksum"]
    assert export_client.get(API + f"/exports/{exported['id']}/download").content == download.content
    assert test_db.scalar(select(func.count()).select_from(WorkshopExport)) == 2


@pytest.mark.parametrize("failure", ["storage", "database"])
def test_failed_generation_leaves_no_success_row_or_file(export_client, test_db, monkeypatch, failure):
    _, snapshot = confirmed(export_client)
    def fail(*args, **kwargs):
        if failure == "storage":
            raise OSError("PRIVATE TEST PATH")
        raise OperationalError("fictional", {}, RuntimeError("PRIVATE TEST VALUE"))
    with monkeypatch.context() as patch:
        patch.setattr(os if failure == "storage" else test_db, "open" if failure == "storage" else "commit", fail)
        result = export_client.post(API + f"/revisions/{snapshot['id']}/exports")
    assert result.status_code == (503 if failure == "storage" else 500) and "PRIVATE TEST" not in result.text
    assert test_db.scalar(select(func.count()).select_from(WorkshopExport)) == 0
    assert not list(settings.WORKSHOP_STORAGE_DIR.iterdir())
    assert export_client.post(API + f"/revisions/{snapshot['id']}/exports").status_code == 200


def test_corrupt_missing_or_unsafe_output_not_reused_or_served(export_client, test_db):
    _, snapshot = confirmed(export_client)
    path = API + f"/revisions/{snapshot['id']}/exports"
    exported = export_client.post(path).json()
    stored = test_db.get(WorkshopExport, UUID(exported["id"]))
    file = settings.WORKSHOP_STORAGE_DIR / stored.storage_key
    file.write_bytes(b"tampered")
    download = API + f"/exports/{exported['id']}/download"
    assert export_client.get(download).status_code == 503
    assert export_client.post(path).status_code == 503
    file.unlink()
    assert export_client.get(download).status_code == 503
    stored.storage_key = "../private.csv"
    test_db.commit()
    assert export_client.get(download).status_code == 503
    assert export_client.get(API + f"/exports/{uuid4()}/download").status_code == 404


def test_disabled_export_gate(export_client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert export_client.post(API + f"/revisions/{uuid4()}/exports").status_code == 404
    assert export_client.get(API + f"/exports/{uuid4()}/download").status_code == 404
