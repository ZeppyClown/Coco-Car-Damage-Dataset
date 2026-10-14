"""Workshop details, running invoice numbers, unique job numbers, expenses, profit and example jobs."""
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db.models import WorkshopExpense, WorkshopInvoice, WorkshopInvoiceCounter, WorkshopJob, WorkshopPayment, WorkshopUser
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
    assert shop.get(API + "/setup").json() | {"form": None} == {"company": None, "jobs": 0, "examples": 0, "form": None}
    first, second = finished(shop, "J-1"), finished(shop, "J-2")
    assert issue(shop, first).status_code == 403
    assert shop.put(API + "/setup", json={**COMPANY, "name": ""}).status_code == 422
    assert shop.put(API + "/setup", json=COMPANY).json() | {"form": None} == {"company": COMPANY, "jobs": 2, "examples": 0, "form": None}
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


def test_example_jobs_can_be_removed_leaving_real_records(shop, test_db):
    assert shop.delete(API + "/setup/example-jobs").status_code == 409
    shop.put(API + "/setup", json=COMPANY)
    examples = shop.post(API + "/setup/example-jobs").json()["examples"]
    assert examples > 40 and shop.get(API + "/setup").json()["examples"] == examples
    real = shop.post(API + "/jobs", json={**EXAMPLE, "data_origin": "private_source", "job_reference": "REAL-1"})
    assert real.status_code == 201
    assert shop.post(API + "/expenses", json={"spent_on": TODAY, "supplier": "Fictional Parts", "category": "parts",
                                              "description": "Real bill", "amount": "50.00", "gst": "0"}).status_code == 201
    state = shop.delete(API + "/setup/example-jobs").json()
    assert state["examples"] == 0 and state["jobs"] == 1
    assert test_db.scalars(select(WorkshopJob.id)).all() == [__import__("uuid").UUID(real.json()["id"])]
    assert [row.description for row in test_db.scalars(select(WorkshopExpense))] == ["Real bill"]
    assert test_db.scalar(select(func.count()).select_from(WorkshopInvoice)) == 0
    assert test_db.scalar(select(func.count()).select_from(WorkshopPayment)) == 0
    assert all(counter.last == 0 for counter in test_db.scalars(select(WorkshopInvoiceCounter)))
    assert shop.delete(API + "/setup/example-jobs").status_code == 409


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


def test_staff_logins_roles_switch_off_and_lockout(shop, test_db):
    from app.core.workshop_auth import FAILURES, MAX_FAILURES
    from tests.conftest import TEST_OPERATOR, TEST_PASSWORD
    owner = (TEST_OPERATOR, TEST_PASSWORD)
    assert shop.get(API + "/users").json() == {"me": owner[0], "role": "owner", "users": [
        {"username": owner[0], "role": "owner", "active": True, "built_in": True}]}
    assert shop.post(API + "/users", json={"username": "mei ling", "password": "short"}).status_code == 422
    assert shop.post(API + "/users", json={"username": owner[0], "password": "long-enough-password"}).status_code == 422
    assert shop.post(API + "/users", json={"username": "bad:name", "password": "long-enough-password"}).status_code == 422
    created = shop.post(API + "/users", json={"username": "meiling", "password": "counter-desk-2026"})
    assert created.status_code == 201 and created.json()[1] == {"username": "meiling", "role": "staff", "active": True, "built_in": False}
    assert "counter-desk-2026" not in created.text and test_db.get(WorkshopUser, "meiling").password_hash.startswith("scrypt$")
    shop.auth = ("meiling", "counter-desk-2026")
    # Staff can do the daily work under their own name, but not change the workshop, the logins or add example jobs.
    assert shop.get(API + "/users").json() == {"me": "meiling", "role": "staff", "users": []}
    job = shop.post(API + "/jobs", json={**EXAMPLE, "job_reference": "S-1"}).json()
    revision = shop.post(API + f"/jobs/{job['id']}/confirm", json={"expected_version": 1, "reviewer": "someone else", "acknowledged": True}).json()
    assert revision["reviewer"] == "meiling"
    for method, path, body in (("put", "/setup", COMPANY), ("post", "/setup/example-jobs", None),
                               ("post", "/users", {"username": "x", "password": "long-enough-password"}),
                               ("post", "/users/meiling/active", {"active": True})):
        assert getattr(shop, method)(API + path, json=body).status_code == 403
    assert shop.put(API + "/setup/form", files={"file": ("form.png", b"x", "image/png")}).status_code == 403
    assert shop.delete(API + "/setup/example-jobs").status_code == 403
    shop.auth = ("meiling", "wrong-password-here")
    assert shop.get(API + "/setup").status_code == 401
    shop.auth = owner
    assert shop.post(API + "/users/meiling/active", json={"active": False}).json()[1]["active"] is False
    assert shop.post(API + "/users/nobody/active", json={"active": False}).status_code == 404
    shop.auth = ("meiling", "counter-desk-2026")
    assert shop.get(API + "/setup").status_code == 401
    # Ten wrong passwords from one address: that address waits, even with the right password.
    FAILURES.clear()
    shop.auth = (owner[0], "wrong-password-here")
    assert [shop.get(API + "/setup").status_code for _ in range(MAX_FAILURES + 1)] == [401] * MAX_FAILURES + [429]
    shop.auth = owner
    assert shop.get(API + "/setup").status_code == 429
    FAILURES.clear()
    assert shop.get(API + "/setup").status_code == 200


def test_blank_form_picture_can_be_uploaded_and_is_used_for_printing(shop, monkeypatch):
    from io import BytesIO
    from PIL import Image
    monkeypatch.setattr(settings, "WORKSHOP_SHEET_TEMPLATE", None)
    picture = BytesIO(); Image.new("RGB", (600, 850), "white").save(picture, "JPEG")
    upload = lambda content: shop.put(API + "/setup/form", files={"file": ("form.jpg", content, "image/jpeg")})
    assert upload(picture.getvalue()).status_code == 409
    assert shop.put(API + "/setup", json=COMPANY).json()["form"] is None
    assert shop.get(API + "/sheet-diagram").status_code == 404
    assert upload(b"not a picture").status_code == 422
    small = BytesIO(); Image.new("RGB", (50, 50)).save(small, "PNG")
    assert upload(small.getvalue()).status_code == 415
    assert upload(picture.getvalue()).json()["form"] == "uploaded"
    outline = shop.get(API + "/sheet-diagram")
    assert outline.status_code == 200 and Image.open(BytesIO(outline.content)).format == "PNG"
    revision = finished(shop, "F-1")
    assert "data:image/png;base64," in shop.get(API + f"/revisions/{revision['id']}/sheet").text
    # Saving the workshop details again keeps the picture.
    assert shop.put(API + "/setup", json=COMPANY).json()["form"] == "uploaded"


def test_hosted_copy_serves_only_the_workshop(shop, monkeypatch):
    assert shop.get("/docs").status_code == 200
    monkeypatch.setattr(settings, "WORKSHOP_ONLY", True)
    shop.auth = None
    assert [shop.get(path, follow_redirects=False).status_code for path in ("/", "/docs", "/openapi.json", "/api/v1/query", "/health")] == [307, 404, 404, 404, 200]
    assert shop.get("/", follow_redirects=False).headers["location"] == "/workshop"
    assert shop.get("/static/workshop.js").status_code == 200 and shop.get("/static/index.html").status_code == 404
    assert shop.get("/workshop", follow_redirects=False).headers["location"] == "/workshop/login"
    assert shop.get("/workshop/login").status_code == 200
