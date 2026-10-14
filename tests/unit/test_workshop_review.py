"""Review gates and preserved history, using fictional/manual sources."""
from copy import deepcopy
import json
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import select, func, update
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.models import WorkshopDocument, WorkshopJobRevision


EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
PREFIX = "/api/v1/workshop/jobs"
REVIEW = {"expected_version": 1, "reviewer": "Fictional reviewer", "acknowledged": True}


@pytest.fixture
def review_client(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    return client


def test_confirmation_is_idempotent_and_quote_remains_quote(review_client, test_db):
    job = review_client.post(PREFIX, json=EXAMPLE).json()
    path = f"{PREFIX}/{job['id']}"
    first = review_client.post(path + "/confirm", json=REVIEW)
    assert first.status_code == 200
    revision = first.json()
    assert revision["record"]["record_stage"] == "quote"
    assert revision["reviewed_at"].endswith("Z")
    repeated = review_client.post(path + "/confirm", json={**REVIEW, "reviewer": "Another fictional name"})
    assert repeated.json() == revision
    assert test_db.scalar(select(func.count()).select_from(WorkshopJobRevision)) == 1
    assert review_client.get(path).json()["draft_version"] == 1


def test_correction_preserves_old_review_and_requires_new_confirmation(review_client):
    job = review_client.post(PREFIX, json=EXAMPLE).json()
    path = f"{PREFIX}/{job['id']}"
    first = review_client.post(path + "/confirm", json=REVIEW).json()
    corrected = deepcopy(job["draft"])
    corrected["items"][0]["description"] = "Fictional corrected description"
    assert review_client.patch(path, json={"expected_version": 1, "draft": corrected}).status_code == 200
    assert review_client.post(path + "/confirm", json=REVIEW).status_code == 409
    assert review_client.get(path + "/revisions").json() == [first]
    second = review_client.post(path + "/confirm", json={**REVIEW, "expected_version": 2}).json()
    assert second["id"] != first["id"] and second["version"] == 2
    assert review_client.get(path + "/revisions", params={"limit": 1}).json() == [second]
    assert review_client.get(path + "/revisions", params={"limit": 1, "offset": 1}).json() == [first]
    assert first["record"]["items"][0]["description"] != second["record"]["items"][0]["description"]


@pytest.mark.parametrize("change", [
    {"record_stage": "unknown"},
    {"manual_provenance": None},
    {"field_states": {"job_reference": "proposed"}},
    {"items": [{"description_raw": "Unclear", "description_state": "unclear"}]},
])
def test_unresolved_draft_cannot_confirm(review_client, test_db, change):
    job = review_client.post(PREFIX, json={**EXAMPLE, **change}).json()
    response = review_client.post(f"{PREFIX}/{job['id']}/confirm", json=REVIEW)
    assert response.status_code == 422
    assert test_db.scalar(select(func.count()).select_from(WorkshopJobRevision)) == 0


@pytest.mark.parametrize("change", [
    {"reviewer": "   "}, {"acknowledged": False}, {"acknowledged": 1},
    {"expected_version": True}, {"reviewed_at": "2025-12-01T00:00:00Z"},
])
def test_invalid_review_request_and_client_timestamp_rejected(review_client, change):
    job = review_client.post(PREFIX, json=EXAMPLE).json()
    assert review_client.post(f"{PREFIX}/{job['id']}/confirm", json={**REVIEW, **change}).status_code == 422


def test_review_failure_rolls_back_and_history_bounds(review_client, test_db, monkeypatch):
    job = review_client.post(PREFIX, json=EXAMPLE).json()
    path = f"{PREFIX}/{job['id']}"
    def fail_commit():
        raise OperationalError("fictional", {}, RuntimeError("PRIVATE TEST VALUE"))
    with monkeypatch.context() as patch:
        patch.setattr(test_db, "commit", fail_commit)
        result = review_client.post(path + "/confirm", json=REVIEW)
    assert result.status_code == 500 and "PRIVATE TEST VALUE" not in result.text
    assert test_db.scalar(select(func.count()).select_from(WorkshopJobRevision)) == 0
    assert review_client.post(path + "/confirm", json=REVIEW).status_code == 200
    assert review_client.get(path + "/revisions", params={"limit": 101}).status_code == 422
    assert review_client.get(path + "/revisions", params={"offset": -1}).status_code == 422
    assert review_client.get(f"{PREFIX}/{uuid4()}/revisions").status_code == 404


def test_missing_stored_source_blocks_review(review_client, test_db, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    png = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    source = review_client.post("/api/v1/workshop/documents", data={"data_origin": "synthetic_demo"}, files={"file": ("demo.png", png, "image/png")}).json()
    job = review_client.post(PREFIX, json={**EXAMPLE, "manual_provenance": None, "source_document_id": source["id"]}).json()
    # An older row whose file is gone from the storage folder.
    test_db.execute(update(WorkshopDocument).values(content=None))
    test_db.commit()
    assert review_client.post(f"{PREFIX}/{job['id']}/confirm", json=REVIEW).status_code == 503
