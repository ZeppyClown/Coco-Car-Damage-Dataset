"""Money, billing boundaries, protected immutable output and retries."""
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from pydantic import ValidationError
import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.db.models import WorkshopInvoice, WorkshopJobRevision
from app.schemas.workshop_invoice import InvoiceRequest, InvoiceSupplier, InvoiceIssueRequest
from app.services.workshop_invoice import calculate_invoice


API = "/api/v1/workshop"
EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]


def billing_request(**changes):
    return {
        "supplier": {"name": "Fictional Workshop", "address": "1 Fictional Street, Singapore (DEMO)",
                     "gst_status": "registered", "gst_registration_number": "FICTIONAL-NOT-A-REGISTRATION"},
        "customer": {"name": "Fictional Customer", "address": "2 Fictional Street (DEMO)"},
        "invoice_date": datetime.now(ZoneInfo("Asia/Singapore")).date().isoformat(),
        "pricing_basis": "inclusive", "discount": "0.00", **changes,
    }


def completed_record(**changes):
    return {**deepcopy(EXAMPLE), "record_stage": "completed_work", **changes}


def calculate(amounts, **changes):
    record = completed_record()
    record["items"] = [{"description": "Fictional repair", "description_state": "confirmed",
                        "amount": amount, "amount_state": "confirmed"} for amount in amounts]
    return calculate_invoice(WorkshopJobRevision(id=uuid4(), job_id=uuid4(), record=record),
                             InvoiceRequest.model_validate(billing_request(**changes))).model_dump(mode="json")


@pytest.mark.parametrize("amounts,basis,discount,net,gst,total", [
    (["109.00"], "inclusive", "0.00", "100.00", "9.00", "109.00"),
    (["100.00"], "exclusive", "0.00", "100.00", "9.00", "109.00"),
    (["25.10"], "inclusive", "0.00", "23.03", "2.07", "25.10"),
    (["1.28"] * 3, "exclusive", "0.00", "3.84", "0.35", "4.19"),
    (["0.50"], "exclusive", "0.00", "0.50", "0.05", "0.55"),
    (["109.00"], "inclusive", "10.90", "90.00", "8.10", "98.10"),
    (["100.00"], "exclusive", "10.00", "90.00", "8.10", "98.10"),
    (["0.00"], "inclusive", "0.00", "0.00", "0.00", "0.00"),
    (["1.00"], "inclusive", "1.00", "0.00", "0.00", "0.00"),
])
def test_exact_money_and_subtotal_rounding(amounts, basis, discount, net, gst, total):
    result = calculate(amounts, pricing_basis=basis, discount=discount)
    assert (result["net"], result["gst"], result["total"]) == (net, gst, total)


def test_nonregistered_is_not_zero_rated_and_discount_cannot_exceed_subtotal():
    supplier = billing_request()["supplier"]
    supplier.update(gst_status="not_registered", gst_registration_number=None)
    result = calculate(["109.00"], supplier=supplier)
    assert (result["gst_rate"], result["net"], result["gst"], result["total"]) == ("not_applicable", "109.00", "0.00", "109.00")
    with pytest.raises(HTTPException) as error:
        calculate(["1.00"], discount="1.01")
    assert error.value.status_code == 422
    with pytest.raises(HTTPException):
        calculate(["9999999999.99"], pricing_basis="exclusive")
    with pytest.raises(HTTPException):
        calculate(["9999999999.99", "1.00"])


@pytest.mark.parametrize("discount", [0.1, True, "NaN", "-0.01", "0.001"])
def test_invalid_discount_rejected(discount):
    with pytest.raises(ValidationError):
        InvoiceRequest.model_validate(billing_request(discount=discount))


@pytest.mark.parametrize("change", [
    {"gst_status": "unknown"}, {"gst_registration_number": None},
    {"gst_status": "not_registered"}, {"address": " "},
])
def test_supplier_details_are_required_without_assumed_registration(change):
    data = billing_request()
    data["supplier"].update(change)
    with pytest.raises(ValidationError):
        InvoiceRequest.model_validate(data)


@pytest.mark.parametrize("ack", [False, "true", 1, None])
def test_issue_ack_is_strict(ack):
    with pytest.raises(ValidationError):
        InvoiceIssueRequest.model_validate({"invoice": billing_request(), "acknowledged": ack})


@pytest.fixture
def billing_client(client, monkeypatch):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_REAL_INVOICES_ENABLED", False)
    monkeypatch.setattr(settings, "WORKSHOP_BILLING_SUPPLIER", None)
    return client


def reviewed(client, record=None):
    job = client.post(API + "/jobs", json=record or completed_record()).json()
    response = client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 1, "reviewer": "Client spoof ignored", "acknowledged": True,
    })
    assert response.status_code == 200
    return job, response.json()


def issue(client, revision, request=None):
    return client.post(API + f"/revisions/{revision['id']}/invoice", json={
        "invoice": request or billing_request(), "acknowledged": True,
    })


def test_preview_issue_reopen_retry_html_and_corrections(billing_client, test_db):
    record = completed_record()
    record["items"].append({"description_raw": "Cancelled example", "amount_raw": "900.00", "cancelled": True})
    job, revision = reviewed(billing_client, record)
    request = billing_request()
    request["customer"]["name"] = '<script>alert("DEMO")</script>示例'
    preview = billing_client.post(API + f"/revisions/{revision['id']}/invoice-preview", json=request)
    assert preview.status_code == 200 and preview.json()["gst"] == "2.07"
    assert len(preview.json()["lines"]) == 1
    assert test_db.scalar(select(func.count()).select_from(WorkshopInvoice)) == 0
    first = issue(billing_client, revision, request)
    assert first.status_code == 200
    invoice = first.json()
    assert invoice["number"].startswith("DEMO-INV-") and invoice["issued_by"] == "fictional-test-operator"
    assert issue(billing_client, revision, request).json() == invoice
    assert billing_client.get(API + f"/jobs/{job['id']}/invoice").json() == invoice
    assert billing_client.get(API + f"/invoices/{invoice['id']}").json() == invoice
    printed = billing_client.get(API + f"/invoices/{invoice['id']}/print")
    assert printed.headers["cache-control"] == "no-store" and "default-src 'none'" in printed.headers["content-security-policy"]
    assert sha256(printed.content).hexdigest() == invoice["checksum"]
    assert '<script>' not in printed.text and '&lt;script&gt;' in printed.text and "示例" in printed.text
    assert "Cancelled example" not in printed.text and "DEMO ONLY" in printed.text and "Tax Invoice" in printed.text
    assert issue(billing_client, revision, {**request, "discount": "1.00"}).status_code == 409
    corrected = {**job["draft"], "job_reference": "DEMO-CORRECTION"}
    billing_client.patch(API + f"/jobs/{job['id']}", json={"expected_version": 1, "draft": corrected})
    new = billing_client.post(API + f"/jobs/{job['id']}/confirm", json={"expected_version": 2, "reviewer": "Fictional", "acknowledged": True}).json()
    assert issue(billing_client, new, request).status_code == 409
    assert issue(billing_client, revision, request).json() == invoice
    assert billing_client.get(API + f"/invoices/{invoice['id']}/print").content == printed.content
    assert test_db.scalar(select(func.count()).select_from(WorkshopInvoice)) == 1


@pytest.mark.parametrize("changes", [
    {"record_stage": "quote"}, {"record_stage": "approved_scope"}, {"currency": "USD"},
    {"items": [{"description": "Unknown price", "description_state": "confirmed"}]},
])
def test_billing_rejects_nonbillable_records(billing_client, changes):
    record = completed_record(**changes)
    record["field_states"]["currency"] = "confirmed"
    _, revision = reviewed(billing_client, record)
    assert issue(billing_client, revision).status_code == 422


def test_stale_draft_unreviewed_missing_ids_dates_and_extra_fields(billing_client):
    job, revision = reviewed(billing_client)
    assert issue(billing_client, {"id": job["id"]}).status_code == 404
    assert issue(billing_client, revision, billing_request(invoice_date="2024-01-01")).status_code == 422
    assert issue(billing_client, revision, {**billing_request(), "total": "0.00"}).status_code == 422
    billing_client.patch(API + f"/jobs/{job['id']}", json={"expected_version": 1, "draft": job["draft"]})
    assert issue(billing_client, revision).status_code == 409
    assert billing_client.get(API + f"/invoices/{uuid4()}").status_code == 404


def test_real_issuance_gate_and_supplier_profile(billing_client, monkeypatch):
    _, revision = reviewed(billing_client, completed_record(data_origin="private_source"))
    assert issue(billing_client, revision).status_code == 403
    monkeypatch.setattr(settings, "WORKSHOP_REAL_INVOICES_ENABLED", True)
    assert issue(billing_client, revision).status_code == 503
    supplier = InvoiceSupplier.model_validate(billing_request()["supplier"])
    monkeypatch.setattr(settings, "WORKSHOP_BILLING_SUPPLIER", supplier)
    request = billing_request()
    request["supplier"]["name"] = "Forged supplier"
    assert issue(billing_client, revision, request).status_code == 422
    assert billing_client.get(API + "/billing-settings").json()["supplier"] == supplier.model_dump(mode="json")
    response = issue(billing_client, revision)
    assert response.status_code == 200 and response.json()["number"].startswith("INV-")


def test_failed_commit_has_no_partial_invoice_and_retry_works(billing_client, test_db, monkeypatch):
    _, revision = reviewed(billing_client)
    def fail():
        raise OperationalError("fictional", {}, RuntimeError("PRIVATE BILLING INPUT"))
    with monkeypatch.context() as patch:
        patch.setattr(test_db, "commit", fail)
        result = issue(billing_client, revision)
    assert result.status_code == 500 and "PRIVATE BILLING INPUT" not in result.text
    assert test_db.scalar(select(func.count()).select_from(WorkshopInvoice)) == 0
    assert issue(billing_client, revision).status_code == 200


def test_auth_cross_origin_disabled_and_corrupt_output(billing_client, test_db, monkeypatch):
    _, revision = reviewed(billing_client)
    invoice = issue(billing_client, revision).json()
    path = API + f"/invoices/{invoice['id']}/print"
    assert billing_client.get(path, auth=("wrong", "wrong")).status_code == 401
    assert billing_client.post(API + f"/revisions/{revision['id']}/invoice", headers={"Origin": "https://evil.example"}, json={}).status_code == 403
    stored = test_db.get(WorkshopInvoice, UUID(invoice["id"]))
    stored.html = "tampered SQLite test"
    test_db.commit()
    assert billing_client.get(path).status_code == 503 and issue(billing_client, revision).status_code == 503
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", False)
    assert billing_client.get(path).status_code == 404
    assert billing_client.get(API + "/billing-settings").status_code == 404


def test_pre2024_preview_rejected_and_written_totals_not_guessed():
    with pytest.raises(HTTPException):
        calculate(["109.00"], invoice_date="2023-12-31")
    record = completed_record(written_total="900.00", written_adjustment="-9.00", written_grand_total="891.00")
    record["field_states"].update(written_total="confirmed", written_adjustment="confirmed", written_grand_total="confirmed")
    result = calculate_invoice(WorkshopJobRevision(id=uuid4(), job_id=uuid4(), record=record), InvoiceRequest.model_validate(billing_request()))
    assert str(result.total) == "25.10" and str(result.gst) == "2.07"
