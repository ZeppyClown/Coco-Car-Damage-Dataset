"""Fictional local API checks, isolated from application storage/providers."""
from copy import deepcopy
import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.models import WorkshopDocument, WorkshopJob


EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
PREFIX = "/api/v1/workshop/jobs"


@pytest.fixture
def workshop_client(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    return client


def test_routes_disabled_by_default(client, monkeypatch, test_db):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert client.post(PREFIX, json=EXAMPLE).status_code == 404
    assert client.get(f"{PREFIX}/{uuid4()}").status_code == 404
    assert client.patch(f"{PREFIX}/{uuid4()}", json={"expected_version": 1, "draft": EXAMPLE}).status_code == 404
    assert test_db.scalar(select(func.count()).select_from(WorkshopJob)) == 0


def test_create_read_replace_and_stale_save(workshop_client):
    created = workshop_client.post(PREFIX, json=EXAMPLE)
    assert created.status_code == 201
    job = created.json()
    assert job["draft_version"] == 1 and job["draft"]["items"][0]["amount"] == "25.10"
    path = f"{PREFIX}/{job['id']}"
    assert workshop_client.get(path).json()["draft"] == job["draft"]
    draft = deepcopy(job["draft"])
    draft["items"][0].update(amount=None, amount_state="unclear", amount_raw="8?")
    draft["diagram_notes_raw"] = "示例 / fictional note"
    saved = workshop_client.patch(path, json={"expected_version": 1, "draft": draft})
    assert saved.status_code == 200 and saved.json()["draft_version"] == 2
    assert saved.json()["draft"]["items"][0]["amount"] is None
    assert workshop_client.patch(path, json={"expected_version": 1, "draft": EXAMPLE}).status_code == 409
    assert workshop_client.get(path).json()["draft"]["diagram_notes_raw"] == draft["diagram_notes_raw"]


def test_incomplete_drafts_and_same_customer_jobs_are_separate(workshop_client):
    empty = workshop_client.post(PREFIX, json={"data_origin": "synthetic_demo"})
    assert empty.status_code == 201 and empty.json()["draft"]["record_stage"] == "unknown"
    left = workshop_client.post(PREFIX, json=EXAMPLE).json()
    right = workshop_client.post(PREFIX, json={**EXAMPLE, "job_reference": "DEMO-JOB-001B"}).json()
    assert left["id"] != right["id"]
    assert left["draft"]["customer_reference"] == right["draft"]["customer_reference"]


def test_source_exists_matches_origin_and_origin_cannot_change(workshop_client, test_db):
    data = deepcopy(EXAMPLE)
    data["source_document_id"] = str(uuid4())
    assert workshop_client.post(PREFIX, json=data).status_code == 422
    document = WorkshopDocument(checksum="a" * 64, storage_key="fictional-test.png", media_type="image/png", byte_size=1, data_origin="synthetic_demo")
    test_db.add(document)
    test_db.commit()
    data["source_document_id"] = str(document.id)
    assert workshop_client.post(PREFIX, json={**data, "data_origin": "private_source"}).status_code == 422
    job = workshop_client.post(PREFIX, json=data).json()
    assert test_db.get(WorkshopJob, UUID(job["id"])).source_document_id == document.id
    path = f"{PREFIX}/{job['id']}"
    assert workshop_client.patch(path, json={"expected_version": 1, "draft": {**data, "source_document_id": None, "data_origin": "private_source"}}).status_code == 422
    assert workshop_client.get(path).json()["draft_version"] == 1


@pytest.mark.parametrize("payload", [
    {"expected_version": 0, "draft": EXAMPLE},
    {"expected_version": True, "draft": EXAMPLE},
    {"expected_version": 1, "draft": {"data_origin": "synthetic_demo", "invoice_paid": True}},
])
def test_invalid_update_does_not_write(workshop_client, payload):
    job = workshop_client.post(PREFIX, json=EXAMPLE).json()
    path = f"{PREFIX}/{job['id']}"
    assert workshop_client.patch(path, json=payload).status_code == 422
    assert workshop_client.get(path).json()["draft_version"] == 1


def test_unknown_job_and_malformed_uuid(workshop_client):
    path = f"{PREFIX}/{uuid4()}"
    assert workshop_client.get(path).status_code == 404
    assert workshop_client.patch(path, json={"expected_version": 1, "draft": EXAMPLE}).status_code == 404
    assert workshop_client.get(f"{PREFIX}/not-a-uuid").status_code == 422


def test_commit_failure_rolls_back_and_hides_database_detail(workshop_client, test_db, monkeypatch):
    def fail_commit():
        raise OperationalError("fictional statement", {}, RuntimeError("PRIVATE TEST VALUE"))
    with monkeypatch.context() as patch:
        patch.setattr(test_db, "commit", fail_commit)
        response = workshop_client.post(PREFIX, json=EXAMPLE)
    assert response.status_code == 500 and "PRIVATE TEST VALUE" not in response.text
    assert test_db.scalar(select(func.count()).select_from(WorkshopJob)) == 0
    assert workshop_client.post(PREFIX, json=EXAMPLE).status_code == 201
