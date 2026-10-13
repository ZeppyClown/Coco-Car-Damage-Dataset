"""Workshop details, running invoice numbers, unique job numbers, expenses, profit and example jobs."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import WorkshopInvoice, WorkshopInvoiceCounter, WorkshopJob
from app.schemas.workshop import WorkshopDraft
from app.services.workshop_extraction import extraction_schema

EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
API = "/api/v1/workshop"
TODAY = datetime.now(ZoneInfo("Asia/Singapore")).date().isoformat()
COMPANY = {"name": "Fictional Motor Works", "address": "1 Fictional Street", "gst_registration_number": "M2-0000000-0", "phone": "6000 0000"}
SUPPLIER = {"name": COMPANY["name"], "address": COMPANY["address"], "gst_status": "registered",
            "gst_registration_number": COMPANY["gst_registration_number"]}


@pytest.fixture
def shop(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_REAL_INVOICES_ENABLED", False)
    monkeypatch.setattr(settings, "WORKSHOP_BILLING_SUPPLIER", None)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    return client


def finished(client, reference, origin="private_source"):
    record = {**deepcopy(EXAMPLE), "data_origin": origin, "record_stage": "completed_work", "job_reference": reference}
    job = client.post(API + "/jobs", json=record)
    assert job.status_code == 201, job.text
    return client.post(API + f"/jobs/{job.json()['id']}/confirm", json={"expected_version": 1, "reviewer": "x", "acknowledged": True}).json()


def issue(client, revision, supplier=SUPPLIER):
    return client.post(API + f"/revisions/{revision['id']}/invoice", json={"acknowledged": True, "invoice": {
        "supplier": supplier, "customer": {"name": "Fictional Customer", "address": "2 Fictional Street"},
        "invoice_date": TODAY, "pricing_basis": "inclusive", "discount": "0.00"}})


def test_saved_workshop_details_unlock_invoices_with_running_numbers(shop):
    assert shop.get(API + "/setup").json() == {"company": None, "jobs": 0}
    first, second = finished(shop, "J-1"), finished(shop, "J-2")
    assert issue(shop, first).status_code == 403
    assert shop.put(API + "/setup", json={**COMPANY, "name": ""}).status_code == 422
    assert shop.put(API + "/setup", json=COMPANY).json() == {"company": COMPANY, "jobs": 2}
    assert shop.get(API + "/billing-settings").json() == {"real_invoices_enabled": True, "supplier": SUPPLIER}
    assert issue(shop, first, {**SUPPLIER, "name": "Someone else"}).status_code == 422
    year = TODAY[:4]
    assert [issue(shop, revision).json()["number"] for revision in (first, second, first)] == [
        f"INV-{year}-0001", f"INV-{year}-0002", f"INV-{year}-0001"]
    printed = shop.get(API + f"/invoices/{issue(shop, first).json()['id']}/print").text
    assert "DEMO ONLY" not in printed and "Fictional Motor Works" in printed and "M2-0000000-0" in printed
    # Changing the details later does not rewrite an issued invoice.
    shop.put(API + "/setup", json={**COMPANY, "gst_registration_number": None})
    assert shop.get(API + "/billing-settings").json()["supplier"]["gst_status"] == "not_registered"
    assert "M2-0000000-0" in shop.get(API + f"/jobs/{first['job_id']}/invoice").json()["preview"]["request"]["supplier"]["gst_registration_number"]


def test_job_number_cannot_be_used_twice(shop, test_db):
    one = shop.post(API + "/jobs", json={**EXAMPLE, "job_reference": "JOB 0007"}).json()
    clash = shop.post(API + "/jobs", json={**EXAMPLE, "job_reference": "job-0007"})
    assert clash.status_code == 409 and "already used" in clash.json()["detail"]
    other = shop.post(API + "/jobs", json={**EXAMPLE, "job_reference": "JOB 0008"}).json()
    moved = shop.patch(API + f"/jobs/{other['id']}", json={"expected_version": 1, "draft": {**other["draft"], "job_reference": "JOB0007"}})
    assert moved.status_code == 409 and shop.get(API + f"/jobs/{other['id']}").json()["draft_version"] == 1
    # The job keeps its own number when saved again, and jobs without a number are not compared.
    assert shop.patch(API + f"/jobs/{one['id']}", json={"expected_version": 1, "draft": one["draft"]}).status_code == 200
    blank = {"data_origin": "private_source"}
    assert [shop.post(API + "/jobs", json=blank).status_code for _ in range(2)] == [201, 201]
    assert test_db.scalar(select(func.count()).select_from(WorkshopJob).where(WorkshopJob.job_number == "JOB0007")) == 1


def test_expenses_and_profit_for_the_month(shop):
    shop.put(API + "/setup", json=COMPANY)
    record = finished(shop, "J-9")
    assert issue(shop, record).status_code == 200
    def spend(**values):
        return shop.post(API + "/expenses", json={"spent_on": TODAY, "supplier": "Fictional Parts", "category": "parts", **values})
    assert spend(amount="0.00").status_code == 422 and spend(amount="10.00", gst="11.00").status_code == 422
    assert spend(amount="10.90", gst="0.90", description="Oil filter", job_reference="j 9").status_code == 201
    assert spend(amount="5.00", category="rent").status_code == 201
    assert spend(amount="-1.09", gst="0.09", description="Supplier credit").status_code == 201
    month = TODAY[:7]
    sheet = shop.get(API + "/expenses", params={"month": month}).json()
    assert sheet["totals"] == {"amount": "14.81", "gst": "0.81", "net": "14.00"} and len(sheet["rows"]) == 3
    assert shop.get(API + "/expenses", params={"month": "2020-01"}).json()["rows"] == []
    csv_text = shop.get(API + "/expenses", params={"month": month, "format": "csv"}).content.decode("utf-8-sig")
    assert csv_text.splitlines()[0].startswith("Date,Supplier,Type") and csv_text.splitlines()[-1] == "TOTAL,,,,,,14.81,0.81,14.00"
    profit = shop.get(API + "/profit", params={"month": month}).json()
    # The fixture job is one line of 25.10 including GST: 23.03 before GST, 2.07 GST.
    # Only the expense typed against job J-9 (10.00 before GST) counts as that job's cost; "j 9" finds the same job.
    assert spend(amount="1.00", job_reference="NO-SUCH-JOB").status_code == 422
    assert [(job["job_reference"], job["charged"], job["cost"], job["profit"]) for job in profit["jobs"]] == [("J-9", "23.03", "10.00", "13.03")]
    assert profit | {"costs": None, "jobs": None} == {
        "month": month, "sales": "23.03", "costs": None, "total_costs": "14.00", "profit": "9.03", "gst_collected": "2.07",
        "gst_paid": "0.81", "gst_owed": "1.26", "money_in": "0.00", "money_out": "14.81", "unpaid_invoices": "25.10", "jobs": None}
    assert profit["costs"] == [{"category": "parts", "label": "Parts", "amount": "9.00"}, {"category": "rent", "label": "Rent", "amount": "5.00"}]


def test_accident_details_are_kept_and_never_sent_to_the_ai(shop):
    accident = {"claim_type": "own_damage", "accident_date": "2026-10-01", "insurer": "Fictional Insurer", "excess": "600.00"}
    job = shop.post(API + "/jobs", json={**EXAMPLE, "accident": accident}).json()
    assert job["draft"]["accident"] | accident == job["draft"]["accident"] and job["draft"]["accident"]["other_vehicle"] is None
    assert shop.post(API + "/jobs", json={**EXAMPLE, "job_reference": "X2", "accident": {"claim_type": "fraud"}}).status_code == 422
    assert WorkshopDraft(data_origin="private_source").accident is None
    schema = extraction_schema()
    assert "accident" not in schema["properties"] and "AccidentDetails" not in schema["$defs"]


def test_example_jobs_fill_the_books_once(shop, test_db):
    assert shop.post(API + "/setup/example-jobs").status_code == 409
    shop.put(API + "/setup", json=COMPANY)
    state = shop.post(API + "/setup/example-jobs")
    assert state.status_code == 201 and state.json()["jobs"] > 40
    assert shop.post(API + "/setup/example-jobs").status_code == 409
    month = TODAY[:7]
    numbers = [number for number in test_db.scalars(select(WorkshopInvoice.number).order_by(WorkshopInvoice.number))]
    year = numbers[0][4:8]
    assert len(numbers) > 15 and numbers == [f"INV-{year}-{count:04d}" for count in range(1, len(numbers) + 1)]
    assert test_db.get(WorkshopInvoiceCounter, int(year)).last == len(numbers)
    invoice = test_db.scalars(select(WorkshopInvoice)).first()
    assert invoice.snapshot["request"]["supplier"]["name"] == COMPANY["name"]
    assert shop.get(API + f"/invoices/{invoice.id}/sheet").status_code in (200, 503)
    profit = shop.get(API + "/profit", params={"month": month}).json()
    assert float(profit["total_costs"]) > 0 and float(profit["sales"]) > 0
    assert profit["jobs"] and all(float(job["cost"]) > 0 for job in profit["jobs"])
    found = shop.get(API + "/jobs", params={"q": "Knock"}).json()["results"]
    assert found and any(result["record"]["accident"] for result in shop.get(API + "/jobs", params={"limit": 100}).json()["results"])
