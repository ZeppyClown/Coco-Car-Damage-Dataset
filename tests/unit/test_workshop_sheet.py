"""Reviewed record printed onto the workshop's own job-sheet layout."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import UUID

import pytest

from app.core.config import settings
from app.schemas.workshop import WorkshopRevisionResponse
from app.services.workshop_sheet import ROWS_PER_SHEET, render_job_sheet


EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
API = "/api/v1/workshop"
FAKE_FORM = b"\x89PNG\r\n\x1a\nfictional-blank-form"


def revision(**changes):
    return WorkshopRevisionResponse(
        id=UUID(int=1), job_id=UUID(int=2), version=3, record={**deepcopy(EXAMPLE), **changes},
        reviewer="Fictional reviewer", reviewed_at=datetime(2026, 10, 11, tzinfo=timezone.utc),
    )


def item(text, amount=None, **changes):
    return {"description_raw": text, "description": text, "description_state": "confirmed",
            **({"amount_raw": amount, "amount": amount, "amount_state": "confirmed"} if amount else {}), **changes}


def test_reviewed_values_sit_on_the_paper_form():
    extra = {"make": "Fictional", "model": "Model A", "date_in": "2026-10-01", "date_out": "2026-10-03",
             "quotation_date": "2026-10-01"}
    states = {**EXAMPLE["field_states"], **{name: "confirmed" for name in extra}}
    html = render_job_sheet(revision(**extra, field_states=states), FAKE_FORM)
    assert html.count('<section class="sheet">') == 1 and "data:image/png;base64," in html
    for value in ("DEMO-VEHICLE-A", "Fictional Example Person", "Fictional Model A",
                  "01/10/2026", "03/10/2026", "Example filter replacement", "25.10"):
        assert value in html
    assert "DEMO ONLY" in html


def test_missing_form_still_prints_and_says_so():
    html = render_job_sheet(revision(), None)
    assert "<img" not in html and "Blank job-sheet image is not configured" in html
    assert "Example filter replacement" in html


def test_unknown_amount_stays_blank_cancelled_row_is_struck_and_text_is_escaped():
    html = render_job_sheet(revision(items=[
        item("<script>alert(1)</script> 示例"),
        {"description_raw": "Crossed out", "amount_raw": "80", "description": "Unreviewed meaning",
         "description_state": "proposed", "amount": "80.00", "amount_state": "proposed", "cancelled": True},
    ]), FAKE_FORM)
    assert "<script>" not in html and "&lt;script&gt;alert(1)&lt;/script&gt; 示例" in html
    assert '<s>Crossed out</s>' in html and "Unreviewed meaning" not in html and "80.00" not in html
    assert html.count('class="amount" style="top:22.90%"></span>') == 1
    assert html.count('class="amount" style="top:26.00%"></span>') == 1


def test_more_rows_than_the_form_holds_continue_on_another_sheet():
    html = render_job_sheet(revision(items=[item(f"Row {n}", "1.00") for n in range(ROWS_PER_SHEET + 1)]), FAKE_FORM)
    assert html.count('<section class="sheet">') == 2 and "Sheet 2 of 2" in html
    assert f"Row {ROWS_PER_SHEET}" in html


@pytest.fixture
def sheet_client(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    form = tmp_path / "form.png"
    form.write_bytes(FAKE_FORM)
    monkeypatch.setattr(settings, "WORKSHOP_SHEET_TEMPLATE", form)
    return client


def test_sheet_route_serves_reviewed_versions_only(sheet_client, monkeypatch, test_db):
    job = sheet_client.post(API + "/jobs", json=EXAMPLE).json()
    assert sheet_client.get(API + f"/revisions/{job['id']}/sheet").status_code == 404
    snapshot = sheet_client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 1, "reviewer": "Fictional reviewer", "acknowledged": True}).json()
    page = sheet_client.get(API + f"/revisions/{snapshot['id']}/sheet")
    assert page.status_code == 200 and page.headers["cache-control"] == "no-store"
    assert "img-src data:" in page.headers["content-security-policy"]
    assert "Example filter replacement" in page.text and "data:image/png;base64," in page.text

    monkeypatch.setattr(settings, "WORKSHOP_SHEET_TEMPLATE", Path(""))
    blank = sheet_client.get(API + f"/revisions/{snapshot['id']}/sheet")
    assert blank.status_code == 200 and "not configured" in blank.text
    monkeypatch.setattr(settings, "WORKSHOP_SHEET_TEMPLATE", Path("/nonexistent/form.png"))
    assert sheet_client.get(API + f"/revisions/{snapshot['id']}/sheet").status_code == 503
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert sheet_client.get(API + f"/revisions/{snapshot['id']}/sheet").status_code == 404
