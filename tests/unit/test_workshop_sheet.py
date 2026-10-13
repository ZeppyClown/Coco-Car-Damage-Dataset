"""Reviewed record printed onto the workshop's own job-sheet layout."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import UUID
from zoneinfo import ZoneInfo

import pytest

from app.core.config import settings
from app.db.models import WorkshopInvoice, WorkshopJobRevision
from app.schemas.workshop import WorkshopRevisionResponse
from app.schemas.workshop_invoice import InvoiceRequest, InvoiceResponse
from app.services.workshop_invoice import calculate_invoice
from app.services.workshop_sheet import ROWS_PER_SHEET, render_invoice_sheet, render_job_sheet


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


def billing(**changes):
    return {
        "supplier": {"name": "Fictional Workshop", "address": "1 Fictional Street, Singapore (DEMO)",
                     "gst_status": "registered", "gst_registration_number": "FICTIONAL-NOT-A-REGISTRATION"},
        "customer": {"name": "Fictional Customer", "address": "2 Fictional Street (DEMO)"},
        "invoice_date": "2026-10-12", "pricing_basis": "inclusive", "discount": "0.00", **changes,
    }


def invoice(amounts, **changes):
    record = {**deepcopy(EXAMPLE), "record_stage": "completed_work",
              "items": [item(f"Line {n}", amount) for n, amount in enumerate(amounts, 1)]}
    snapshot = WorkshopJobRevision(id=UUID(int=1), job_id=UUID(int=2), version=1, record=record,
                                   reviewer="Fictional reviewer", reviewed_at=datetime(2026, 10, 11, tzinfo=timezone.utc))
    preview = calculate_invoice(snapshot, InvoiceRequest.model_validate(billing(**changes)))
    response = InvoiceResponse(id=UUID(int=3), number="DEMO-INV-1", preview=preview, issued_by="fictional-operator",
                               issued_at=datetime(2026, 10, 12, tzinfo=timezone.utc), checksum="0" * 64)
    return render_invoice_sheet(response, revision(**record).record, FAKE_FORM)


def test_invoice_uses_the_form_with_totals_in_the_last_rows():
    html = invoice(["109.00"])
    assert html.count('<section class="sheet">') == 1
    for value in ("TAX INVOICE", "No: DEMO-INV-1", "Date: 12/10/2026", "Fictional Customer", "Line 1",
                  "Prices are GST-inclusive.", "DEMO ONLY"):
        assert value in html
    last_three = [f"top:{22.9 + 3.1 * index:.2f}%" for index in (17, 18, 19)]
    for position, label, amount in zip(last_three, ("TOTAL", "GST 9%", "GRAND TOTAL"), ("100.00", "9.00", "109.00")):
        assert f'<span class="item" style="{position}"><b class="total">{label}</b></span>' in html
        assert f'<span class="amount" style="{position}">{amount}</span>' in html


def test_invoice_discount_non_registered_and_overflow():
    html = invoice(["109.00"], discount="9.00")
    assert "LESS DISCOUNT" in html and ">9.00<" in html and ">100.00<" in html
    plain = invoice(["50.00"], supplier={"name": "Fictional Workshop", "address": "1 Fictional Street (DEMO)",
                                         "gst_status": "not_registered"})
    assert "TAX INVOICE" not in plain and "INVOICE\nNo: DEMO-INV-1" in plain and "GST 9%" not in plain and "No GST charged." in plain
    full = invoice(["1.00"] * 18)
    assert full.count('<section class="sheet">') == 2 and full.count("GRAND TOTAL") == 1 and "Sheet 2 of 2" in full


def test_invoice_sheet_route(sheet_client, test_db):
    record = {**deepcopy(EXAMPLE), "record_stage": "completed_work"}
    job = sheet_client.post(API + "/jobs", json=record).json()
    snapshot = sheet_client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 1, "reviewer": "Fictional reviewer", "acknowledged": True}).json()
    today = datetime.now(ZoneInfo("Asia/Singapore")).date().isoformat()
    issued = sheet_client.post(API + f"/revisions/{snapshot['id']}/invoice",
                               json={"invoice": billing(invoice_date=today), "acknowledged": True})
    assert issued.status_code == 200
    page = sheet_client.get(API + f"/invoices/{issued.json()['id']}/sheet")
    assert page.status_code == 200 and "img-src data:" in page.headers["content-security-policy"]
    assert issued.json()["number"] in page.text and "GRAND TOTAL" in page.text and "25.10" in page.text
    assert sheet_client.get(API + f"/invoices/{job['id']}/sheet").status_code == 404
    stored = test_db.get(WorkshopInvoice, UUID(issued.json()["id"]))
    stored.checksum = "0" * 64
    test_db.commit()
    assert sheet_client.get(API + f"/invoices/{issued.json()['id']}/sheet").status_code == 503
