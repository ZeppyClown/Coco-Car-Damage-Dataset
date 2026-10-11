"""Reviewed lookup excludes drafts/obsolete revisions and treats searches literally."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.core.config import settings


API = "/api/v1/workshop/jobs"
EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]


@pytest.fixture
def lookup_client(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    return client


def create(client, reference, *, reviewed=True, customer="Fictional Same Name", vehicle="DEMO-VEHICLE", stage="quote"):
    draft = {**deepcopy(EXAMPLE), "job_reference": reference, "customer_reference": customer, "vehicle_reference": vehicle, "record_stage": stage}
    for name in ("customer_reference", "vehicle_reference"):
        if draft[name] is None: draft["field_states"][name] = "missing"
    job = client.post(API, json=draft).json()
    if reviewed:
        response = client.post(API + f"/{job['id']}/confirm", json={"expected_version": 1, "reviewer": "Fictional", "acknowledged": True})
        assert response.status_code == 200
    return job


def test_latest_reviewed_only_and_newer_draft_distinction(lookup_client):
    first = create(lookup_client, "DEMO-OLD-REFERENCE")
    create(lookup_client, "DEMO-DRAFT-ONLY", reviewed=False)
    new = {**first["draft"], "job_reference": "DEMO-NEW-REFERENCE", "record_stage": "completed_work"}
    lookup_client.patch(API + f"/{first['id']}", json={"expected_version": 1, "draft": new})
    result = lookup_client.get(API).json()["results"]
    assert len(result) == 1 and result[0]["record"]["job_reference"] == "DEMO-OLD-REFERENCE"
    assert result[0]["draft_version"] == 2 and result[0]["has_unreviewed_changes"] is True
    lookup_client.post(API + f"/{first['id']}/confirm", json={"expected_version": 2, "reviewer": "Fictional", "acknowledged": True})
    assert lookup_client.get(API, params={"reference": "OLD"}).json()["results"] == []
    assert lookup_client.get(API, params={"stage": "quote"}).json()["results"] == []
    current = lookup_client.get(API).json()["results"][0]
    assert current["version"] == 2 and current["has_unreviewed_changes"] is False


def test_same_customer_and_vehicle_jobs_remain_distinct_and_paginate(lookup_client):
    jobs = [create(lookup_client, f"DEMO-{number}") for number in range(3)]
    first = lookup_client.get(API, params={"limit": 2, "customer": "same name", "vehicle": "demo-vehicle"}).json()
    second = lookup_client.get(API, params={"limit": 2, "offset": 2}).json()
    assert first["has_more"] is True and second["has_more"] is False
    identities = [r["job_id"] for r in first["results"] + second["results"]]
    assert set(identities) == {job["id"] for job in jobs} and len(identities) == 3


def test_unknown_references_keyword_and_utc_dates_visible(lookup_client):
    job = create(lookup_client, "DEMO-MISSING-REF", customer=None, vehicle=None)
    result = lookup_client.get(API, params={"q": "filter replacement"}).json()["results"][0]
    assert result["record"]["customer_reference"] is None and result["record"]["vehicle_reference"] is None
    day = datetime.fromisoformat(result["reviewed_at"].replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
    assert len(lookup_client.get(API, params={"reviewed_from": day, "reviewed_to": day}).json()["results"]) == 1
    assert lookup_client.get(API, params={"reviewed_to": "2000-01-01"}).json()["results"] == []
    assert lookup_client.get(API, params={"job_id": job["id"]}).json()["results"][0]["job_id"] == job["id"]
    assert lookup_client.get(API, params={"job_id": str(uuid4())}).json()["results"] == []


@pytest.mark.parametrize("text", ["%", "_", "\\", "' OR 1=1 --", '</textarea><img src=x onerror="bad()">', "示例"])
def test_untrusted_queries_are_literal_and_bound(lookup_client, text):
    target = create(lookup_client, "DEMO-TARGET", customer="Fictional " + text)
    create(lookup_client, "DEMO-OTHER", customer="Fictional ordinary")
    for params in ({"customer": text}, {"q": text}):
        result = lookup_client.get(API, params=params)
        assert result.status_code == 200 and [r["job_id"] for r in result.json()["results"]] == [target["id"]]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"q": "x"*201}, {"customer": "x"*201},
                                     {"stage": "invented"}, {"reviewed_from": "invalid"}, {"reviewed_from": "2026-02-01", "reviewed_to": "2026-01-01"}])
def test_invalid_or_unbounded_filters_rejected(lookup_client, params):
    assert lookup_client.get(API, params=params).status_code == 422


def test_empty_and_disabled_lookup(lookup_client, monkeypatch):
    assert lookup_client.get(API, params={"q": "  "}).json() == {"results": [], "limit": 20, "offset": 0, "has_more": False}
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert lookup_client.get(API).status_code == 404
