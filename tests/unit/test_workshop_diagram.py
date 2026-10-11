"""Manual annotations preserve uncertainty; these are fictional meanings only."""
from copy import deepcopy
from datetime import datetime, timezone
import csv
from io import StringIO
import json
from pathlib import Path
from uuid import UUID

import pytest

from app.core.config import settings
from app.db.models import WorkshopJobRevision


API = "/api/v1/workshop"
EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
ACK = {"expected_version": 1, "reviewer": "Fictional annotation reviewer", "acknowledged": True}


@pytest.fixture
def diagram_client(client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    return client


def test_area_only_mark_cannot_create_active_repair(diagram_client):
    record = {**deepcopy(EXAMPLE), "items": [], "diagram_notes_raw": "Fictional mark on a door; operation not stated"}
    job = diagram_client.post(API + "/jobs", json=record).json()
    response = diagram_client.post(API + f"/jobs/{job['id']}/confirm", json=ACK)
    assert response.status_code == 422 and "active item" in response.text
    assert job["draft"]["diagram_notes"] is None and job["draft"]["items"] == []


def test_interpreted_diagram_requires_context_even_with_image(diagram_client):
    png = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    source = diagram_client.post(API + "/documents", data={"data_origin": "synthetic_demo"}, files={"file": ("fictional.png", png, "image/png")}).json()
    record = {**deepcopy(EXAMPLE), "manual_provenance": None, "source_document_id": source["id"],
              "diagram_notes": "Fictional left door location, repair action unknown"}
    record["field_states"]["diagram_notes"] = "confirmed"
    job = diagram_client.post(API + "/jobs", json=record).json()
    response = diagram_client.post(API + f"/jobs/{job['id']}/confirm", json=ACK)
    assert response.status_code == 422 and "clarification context" in response.text


def test_manual_context_cancelled_raw_notes_reviewer_and_stage_survive_output(diagram_client):
    record = deepcopy(EXAMPLE)
    record.update(diagram_notes_raw="Fictional X at door; old action crossed out / 划掉",
                  diagram_notes="Fictional front-left location; operation unknown",
                  manual_provenance="Fictional reviewer explained location using driver-seated-forward convention; no repair operation was established.")
    record["field_states"]["diagram_notes"] = "confirmed"
    record["items"].append({"description_raw":"Fictional crossed-out panel repair", "description":"Unreviewed cancelled meaning",
                            "description_state":"proposed", "amount_raw":"80 crossed out", "amount":"80.00", "amount_state":"proposed", "cancelled":True})
    job = diagram_client.post(API + "/jobs", json=record).json()
    reviewed = diagram_client.post(API + f"/jobs/{job['id']}/confirm", json=ACK)
    assert reviewed.status_code == 200
    snapshot = reviewed.json()
    assert snapshot["reviewer"] == ACK["reviewer"] and snapshot["record"]["record_stage"] == "quote"
    exported = diagram_client.post(API + f"/revisions/{snapshot['id']}/exports").json()
    download = diagram_client.get(API + f"/exports/{exported['id']}/download")
    rows = list(csv.DictReader(StringIO(download.content.decode("utf-8-sig"))))
    assert rows[0]["diagram_notes"] == record["diagram_notes"]
    assert rows[0]["diagram_notes_raw"] == record["diagram_notes_raw"]
    assert rows[0]["manual_provenance"] == record["manual_provenance"] and rows[0]["reviewer"] == ACK["reviewer"]
    assert rows[1]["cancelled"] == "true" and rows[1]["description"] == rows[1]["amount"] == ""
    assert rows[1]["description_raw"] == "Fictional crossed-out panel repair"
    assert diagram_client.get(API + f"/jobs/{job['id']}/revisions").json() == [snapshot]


def test_earlier_review_without_context_stays_readable_and_exportable(diagram_client, test_db):
    png = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    source = diagram_client.post(API + "/documents", data={"data_origin":"synthetic_demo"}, files={"file":("fictional.png",png,"image/png")}).json()
    record = {**deepcopy(EXAMPLE), "manual_provenance":None, "source_document_id":source["id"], "diagram_notes":"Fictional earlier annotation"}
    record["field_states"]["diagram_notes"] = "confirmed"
    job = diagram_client.post(API + "/jobs", json=record).json()
    # Simulate an earlier reviewed snapshot, which the stronger new-confirmation rule cannot rewrite.
    old = WorkshopJobRevision(job_id=UUID(job["id"]), source_document_id=UUID(source["id"]), version=1,
                              record=job["draft"], reviewer="Fictional earlier reviewer", reviewed_at=datetime.now(timezone.utc))
    test_db.add(old); test_db.commit()
    response = diagram_client.get(API + f"/jobs/{job['id']}/revisions")
    assert response.status_code == 200 and response.json()[0]["record"]["diagram_notes"] == record["diagram_notes"]
    assert diagram_client.post(API + f"/revisions/{old.id}/exports").status_code == 200
