"""The books: invoices by month, payments, car history and the pop-up picture guide."""
from copy import deepcopy
import csv
from datetime import datetime
from io import StringIO
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from app.core.config import settings
from app.services.workshop_books import plate_key

EXAMPLE = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())["examples"][0]["record"]
API = "/api/v1/workshop"
TODAY = datetime.now(ZoneInfo("Asia/Singapore")).date().isoformat()


def line(text, amount, section):
    return {"description_raw": text, "description": text, "description_state": "confirmed", "amount_raw": amount,
            "amount": amount, "amount_state": "confirmed", "section": section}


def finished(client, reference, plate, owner, lines, invoice=True):
    record = {**deepcopy(EXAMPLE), "record_stage": "completed_work", "job_reference": reference,
              "vehicle_reference": plate, "customer_reference": owner, "contact": "9000 0000", "make": "Fictional",
              "items": lines, "field_states": {**EXAMPLE["field_states"], "make": "confirmed"}}
    job = client.post(API + "/jobs", json=record).json()
    snapshot = client.post(API + f"/jobs/{job['id']}/confirm", json={
        "expected_version": 1, "reviewer": "x", "acknowledged": True}).json()
    if not invoice:
        return None
    issued = client.post(API + f"/revisions/{snapshot['id']}/invoice", json={"acknowledged": True, "invoice": {
        "supplier": {"name": "Fictional Workshop", "address": "1 Fictional Street (DEMO)", "gst_status": "registered",
                     "gst_registration_number": "FICTIONAL"},
        "customer": {"name": owner, "address": "2 Fictional Street (DEMO)"},
        "invoice_date": TODAY, "pricing_basis": "inclusive", "discount": "0.00"}})
    assert issued.status_code == 200
    return issued.json()


@pytest.fixture
def books(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "WORKSHOP_ENABLED", True)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    return client


def test_month_sheet_adds_up_and_downloads_for_excel(books, test_db):
    first = finished(books, "JOB-1", "SDU 1234 A", "Fictional One", [line("Knock door", "109.00", "knock"), line("Spray door", "218.00", "spray")])
    finished(books, "JOB-2", "SBA 1 Z", "Fictional Two", [line("Oil seal", "54.50", "repair")])
    assert books.post(API + f"/invoices/{first['id']}/payments", json={
        "amount": "300.00", "method": "paynow", "paid_on": TODAY}).status_code == 201
    sheet = books.get(API + "/books", params={"month": TODAY[:7]}).json()
    assert [row["job_reference"] for row in sheet["rows"]] == ["JOB-1", "JOB-2"]
    assert sheet["rows"][0] | {"number": "", "invoice_id": ""} == {
        "invoice_id": "", "number": "", "date": TODAY, "job_reference": "JOB-1", "vehicle": "SDU 1234 A",
        "customer": "Fictional One", "knock": "109.00", "repair": "0.00", "spray": "218.00", "discount": "0.00",
        "net": "300.00", "gst": "27.00", "total": "327.00", "paid": "300.00", "balance": "27.00"}
    assert sheet["totals"] == {"knock": "109.00", "repair": "54.50", "spray": "218.00", "discount": "0.00",
                               "net": "350.00", "gst": "31.50", "total": "381.50", "paid": "300.00", "balance": "81.50"}
    assert books.get(API + "/books", params={"month": "2020-01"}).json()["rows"] == []
    assert books.get(API + "/books", params={"month": "October"}).status_code == 422
    download = books.get(API + "/books", params={"month": TODAY[:7], "format": "csv"})
    assert download.headers["content-type"].startswith("text/csv") and download.content.startswith(b"\xef\xbb\xbf")
    rows = list(csv.reader(StringIO(download.content.decode("utf-8-sig"))))
    assert rows[0][:4] == ["Date", "Invoice no.", "Job no.", "Vehicle no."] and rows[-1][0] == "TOTAL" and rows[-1][-1] == "81.50"


def test_payments_are_added_never_edited_and_refunds_are_negative(books, test_db):
    invoice = finished(books, "JOB-1", "SDU 1234 A", "Fictional One", [line("Knock door", "100.00", "knock")])
    path = API + f"/invoices/{invoice['id']}/payments"
    for bad in ({"amount": "0.00", "method": "cash", "paid_on": TODAY}, {"amount": "10.00", "method": "cheque", "paid_on": TODAY},
                {"amount": "10.005", "method": "cash", "paid_on": TODAY}, {"amount": 10.5, "method": "cash", "paid_on": TODAY}):
        assert books.post(path, json=bad).status_code == 422
    assert books.post(path, json={"amount": "100.00", "method": "cash", "paid_on": TODAY, "note": "at counter"}).status_code == 201
    assert books.post(path, json={"amount": "-20.00", "method": "cash", "paid_on": TODAY, "note": "refund"}).status_code == 201
    state = books.get(path).json()
    assert state["paid"] == "80.00" and state["balance"] == "20.00" and len(state["payments"]) == 2
    assert state["payments"][0]["recorded_by"] and state["payments"][0]["note"] == "at counter"
    assert books.post(API + f"/invoices/{invoice['job_id'] if 'job_id' in invoice else '00000000-0000-0000-0000-000000000000'}/payments",
                      json={"amount": "1.00", "method": "cash", "paid_on": TODAY}).status_code == 404


def test_same_car_is_found_however_the_number_is_typed(books, test_db):
    assert plate_key(" sdu-1234 a ") == plate_key("SDU1234A") == "SDU1234A"
    finished(books, "JOB-1", "SDU 1234 A", "Fictional One", [line("Knock door", "100.00", "knock")])
    finished(books, "JOB-2", "sdu1234a", "Fictional One Tan", [line("Spray door", "200.00", "spray")], invoice=False)
    finished(books, "JOB-3", "SBA 1 Z", "Fictional Two", [line("Oil seal", "50.00", "repair")])
    car = books.get(API + "/vehicles", params={"number": "Sdu 1234a"}).json()
    assert [job["job_reference"] for job in car["jobs"]] == ["JOB-2", "JOB-1"]
    assert car["owner"] == "Fictional One Tan" and car["contact"] == "9000 0000" and car["make"] == "Fictional"
    assert car["jobs"][1]["invoice_total"] == "100.00" and car["jobs"][0]["invoice_total"] is None
    assert car["jobs"][0]["amount"] == "200.00"
    assert books.get(API + "/vehicles", params={"number": "NEW 1"}).json() == {
        "number": "NEW1", "owner": None, "contact": None, "make": None, "model": None, "jobs": []}


def test_picture_guide_lists_and_serves_only_pictures_in_its_folder(books, monkeypatch, tmp_path):
    assert books.get(API + "/guide").json() == []
    guide = tmp_path / "guide"; guide.mkdir()
    (guide / "02 car back.jpg").write_bytes(b"\xff\xd8jpeg"); (guide / "01 job sheet.png").write_bytes(b"\x89PNGpng")
    (guide / "notes.txt").write_text("private"); (tmp_path / "secret.png").write_bytes(b"x")
    monkeypatch.setattr(settings, "WORKSHOP_GUIDE_DIR", guide)
    assert books.get(API + "/guide").json() == ["01 job sheet.png", "02 car back.jpg"]
    picture = books.get(API + "/guide/01 job sheet.png")
    assert picture.status_code == 200 and picture.content == b"\x89PNGpng" and picture.headers["content-type"] == "image/png"
    for name in ("notes.txt", "..%2Fsecret.png", "missing.png"):
        assert books.get(API + "/guide/" + name).status_code == 404
