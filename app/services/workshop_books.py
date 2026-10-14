"""The workshop's books: invoices by month, payments, car history and the picture guide.

This replaces re-typing invoices into a separate spreadsheet: every figure comes from
an issued invoice or a recorded payment.
"""
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path
import re
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import WorkshopExpense, WorkshopGuidePicture, WorkshopInvoice, WorkshopJob, WorkshopJobRevision, WorkshopPayment
from app.schemas.workshop_books import ExpenseRequest, PaymentRequest
from app.services.workshop import number_key
from app.services.workshop_invoice import get_invoice

SECTIONS = ("knock", "repair", "spray")
MONEY_COLUMNS = (*SECTIONS, "discount", "net", "gst", "total", "paid", "balance")
CSV_HEADINGS = ("Date", "Invoice no.", "Job no.", "Vehicle no.", "Customer", "Knock", "Repair & parts", "Spray",
                "Discount", "Total before GST", "GST", "Grand total", "Paid", "Balance")
PICTURES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}


def _money(value) -> str:
    return format(Decimal(value), ".2f")


def plate_key(number: str) -> str:
    """One key per vehicle however staff type the number: letters and digits only, upper case."""
    return re.sub(r"[^A-Z0-9]", "", number.upper())


def _section_sums(record: dict) -> dict[str, Decimal]:
    sums = dict.fromkeys(SECTIONS, Decimal(0))
    for item in record["items"]:
        if not item.get("cancelled") and item.get("amount") is not None:
            sums[item.get("section") or "repair"] += Decimal(item["amount"])
    return sums


def _paid(db: Session, invoice_ids: list[UUID]) -> dict[UUID, Decimal]:
    totals: dict[UUID, Decimal] = {}
    if invoice_ids:
        for payment in db.scalars(select(WorkshopPayment).where(WorkshopPayment.invoice_id.in_(invoice_ids))):
            totals[payment.invoice_id] = totals.get(payment.invoice_id, Decimal(0)) + Decimal(payment.amount)
    return totals


def month_sheet(db: Session, month: str) -> dict:
    # ponytail: reads every invoice and filters by month here; add an invoice_date column if this gets slow.
    invoices = [invoice for invoice in db.scalars(select(WorkshopInvoice).order_by(WorkshopInvoice.issued_at))
                if invoice.snapshot["request"]["invoice_date"].startswith(month)]
    records = {revision.id: revision.record for revision in db.scalars(
        select(WorkshopJobRevision).where(WorkshopJobRevision.id.in_([invoice.revision_id for invoice in invoices])))} if invoices else {}
    paid = _paid(db, [invoice.id for invoice in invoices])
    rows, totals = [], dict.fromkeys(MONEY_COLUMNS, Decimal(0))
    for invoice in invoices:
        snapshot, record = invoice.snapshot, records[invoice.revision_id]
        money = {**_section_sums(record), "discount": Decimal(snapshot["request"]["discount"]), "net": Decimal(snapshot["net"]),
                 "gst": Decimal(snapshot["gst"]), "total": Decimal(snapshot["total"]), "paid": paid.get(invoice.id, Decimal(0))}
        money["balance"] = money["total"] - money["paid"]
        for name in MONEY_COLUMNS:
            totals[name] += money[name]
        rows.append({"invoice_id": str(invoice.id), "number": invoice.number, "date": snapshot["request"]["invoice_date"],
                     "job_reference": snapshot["job_reference"], "vehicle": snapshot["vehicle_reference"] or "",
                     "customer": snapshot["request"]["customer"]["name"], **{name: _money(money[name]) for name in MONEY_COLUMNS}})
    return {"month": month, "rows": rows, "totals": {name: _money(value) for name, value in totals.items()}}


def month_csv(sheet: dict) -> bytes:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(CSV_HEADINGS)
    for row in sheet["rows"]:
        writer.writerow([row["date"], row["number"], row["job_reference"], row["vehicle"], row["customer"],
                         *(row[name] for name in MONEY_COLUMNS)])
    writer.writerow(["TOTAL", "", "", "", "", *(sheet["totals"][name] for name in MONEY_COLUMNS)])
    return b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")


def payments(db: Session, invoice_id: UUID) -> dict:
    invoice = get_invoice(db, invoice_id)
    rows = list(db.scalars(select(WorkshopPayment).where(WorkshopPayment.invoice_id == invoice_id)
                           .order_by(WorkshopPayment.recorded_at)))
    paid = sum((Decimal(row.amount) for row in rows), Decimal(0))
    total = Decimal(invoice.snapshot["total"])
    return {"total": _money(total), "paid": _money(paid), "balance": _money(total - paid), "payments": [
        {"amount": _money(row.amount), "method": row.method, "paid_on": row.paid_on.isoformat(), "note": row.note,
         "recorded_by": row.recorded_by} for row in rows]}


def add_payment(db: Session, invoice_id: UUID, request: PaymentRequest, actor: str) -> dict:
    get_invoice(db, invoice_id)
    try:
        db.add(WorkshopPayment(invoice_id=invoice_id, amount=request.amount, method=request.method, paid_on=request.paid_on,
                               note=request.note, recorded_by=actor, recorded_at=datetime.now(timezone.utc)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return payments(db, invoice_id)


EXPENSE_CATEGORIES = {"parts": "Parts", "paint": "Paint & materials", "subcontract": "Outside work", "wages": "Wages",
                      "rent": "Rent", "utilities": "Utilities", "tools": "Tools & equipment", "other": "Other"}
EXPENSE_HEADINGS = ("Date", "Supplier", "Type", "What for", "Supplier invoice no.", "Job no.", "Paid", "GST in it", "Before GST")


def _month_range(month: str) -> tuple[date, date]:
    year, number = int(month[:4]), int(month[5:])
    return date(year, number, 1), date(year + number // 12, number % 12 + 1, 1)


def expense_sheet(db: Session, month: str) -> dict:
    start, end = _month_range(month)
    rows, totals = [], dict.fromkeys(("amount", "gst", "net"), Decimal(0))
    for row in db.scalars(select(WorkshopExpense).where(WorkshopExpense.spent_on >= start, WorkshopExpense.spent_on < end)
                          .order_by(WorkshopExpense.spent_on, WorkshopExpense.recorded_at)):
        amount, gst = Decimal(row.amount), Decimal(row.gst) * (-1 if row.amount < 0 else 1)
        for name, value in (("amount", amount), ("gst", gst), ("net", amount - gst)):
            totals[name] += value
        rows.append({"date": row.spent_on.isoformat(), "supplier": row.supplier, "category": row.category,
                     "description": row.description, "supplier_invoice": row.supplier_invoice, "job_reference": row.job_reference,
                     "amount": _money(amount), "gst": _money(gst), "net": _money(amount - gst), "recorded_by": row.recorded_by})
    return {"month": month, "rows": rows, "totals": {name: _money(value) for name, value in totals.items()}}


def expense_csv(sheet: dict) -> bytes:
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(EXPENSE_HEADINGS)
    for row in sheet["rows"]:
        writer.writerow([row["date"], row["supplier"], EXPENSE_CATEGORIES[row["category"]], row["description"],
                         row["supplier_invoice"], row["job_reference"], row["amount"], row["gst"], row["net"]])
    writer.writerow(["TOTAL", "", "", "", "", "", *(sheet["totals"][name] for name in ("amount", "gst", "net"))])
    return b"\xef\xbb\xbf" + output.getvalue().encode("utf-8")


def add_expense(db: Session, request: ExpenseRequest, actor: str) -> dict:
    key = number_key(request.job_reference)
    if key and db.scalar(select(WorkshopJob.id).where(WorkshopJob.job_number == key)) is None:
        raise HTTPException(422, f"There is no job no. {request.job_reference.strip()}. Check the number, or leave Job no. empty.")
    try:
        db.add(WorkshopExpense(**request.model_dump(), job_number=key, recorded_by=actor, recorded_at=datetime.now(timezone.utc)))
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return expense_sheet(db, request.spent_on.isoformat()[:7])


def job_profit(db: Session, rows: list[dict]) -> list[dict]:
    """For each invoice: what was charged before GST, what was spent on that job (whenever it was paid), and the difference."""
    keys = {row["invoice_id"]: number_key(row["job_reference"]) for row in rows}
    spent: dict[str, Decimal] = {}
    if rows:
        for expense in db.scalars(select(WorkshopExpense).where(WorkshopExpense.job_number.in_(list(keys.values())))):
            sign = -1 if expense.amount < 0 else 1
            spent[expense.job_number] = spent.get(expense.job_number, Decimal(0)) + Decimal(expense.amount) - sign * Decimal(expense.gst)
    return [{"job_reference": row["job_reference"], "number": row["number"], "vehicle": row["vehicle"], "customer": row["customer"],
             "charged": row["net"], "cost": _money(spent.get(keys[row["invoice_id"]], 0)),
             "profit": _money(Decimal(row["net"]) - spent.get(keys[row["invoice_id"]], Decimal(0)))} for row in rows]


def profit_and_loss(db: Session, month: str) -> dict:
    """Sales less costs for the month, all before GST, plus the GST collected and paid, and the profit on each job."""
    invoices, costs = month_sheet(db, month), expense_sheet(db, month)
    sales = invoices["totals"]
    by_type = dict.fromkeys(EXPENSE_CATEGORIES, Decimal(0))
    for row in costs["rows"]:
        by_type[row["category"]] += Decimal(row["net"])
    start, end = _month_range(month)
    received = sum((Decimal(payment.amount) for payment in db.scalars(
        select(WorkshopPayment).where(WorkshopPayment.paid_on >= start, WorkshopPayment.paid_on < end))), Decimal(0))
    spent = Decimal(costs["totals"]["net"])
    return {"month": month, "sales": sales["net"], "costs": [
                {"category": name, "label": EXPENSE_CATEGORIES[name], "amount": _money(value)} for name, value in by_type.items() if value],
            "total_costs": _money(spent), "profit": _money(Decimal(sales["net"]) - spent),
            "gst_collected": sales["gst"], "gst_paid": costs["totals"]["gst"],
            "gst_owed": _money(Decimal(sales["gst"]) - Decimal(costs["totals"]["gst"])),
            "money_in": _money(received), "money_out": costs["totals"]["amount"],
            "unpaid_invoices": sales["balance"], "jobs": job_profit(db, invoices["rows"])}


def vehicle_history(db: Session, number: str) -> dict:
    key = plate_key(number)
    # ponytail: scans reviewed versions newest first; store a normalised plate column if the archive grows large.
    latest: dict[UUID, WorkshopJobRevision] = {}
    for revision in db.scalars(select(WorkshopJobRevision).order_by(WorkshopJobRevision.reviewed_at.desc(),
                                                                    WorkshopJobRevision.version.desc())):
        if revision.job_id not in latest and key and plate_key(revision.record.get("vehicle_reference") or "") == key:
            latest[revision.job_id] = revision
    invoices = {invoice.job_id: invoice for invoice in db.scalars(
        select(WorkshopInvoice).where(WorkshopInvoice.job_id.in_(list(latest))))} if latest else {}
    newest = next(iter(latest.values())).record if latest else {}
    return {"number": key, "owner": newest.get("customer_reference"), "contact": newest.get("contact"),
            "make": newest.get("make"), "model": newest.get("model"), "jobs": [
                {"job_id": str(job_id), "job_reference": revision.record["job_reference"], "stage": revision.record["record_stage"],
                 "date": (revision.record.get("date_in") or revision.reviewed_at.date().isoformat()),
                 "work": [item["description"] for item in revision.record["items"] if not item.get("cancelled") and item.get("description")],
                 "amount": _money(sum(_section_sums(revision.record).values(), Decimal(0))),
                 "invoice_total": invoices[job_id].snapshot["total"] if job_id in invoices else None}
                for job_id, revision in latest.items()]}


def _guide_folder() -> list[str]:
    folder: Path | None = settings.WORKSHOP_GUIDE_DIR
    if not folder or folder == Path(".") or not folder.is_dir():
        return []
    return [path.name for path in folder.iterdir() if path.is_file() and path.suffix.lower() in PICTURES]


def guide_pictures(db: Session) -> list[str]:
    """Pictures uploaded into the database, plus any in the guide folder on this computer."""
    return sorted(set(_guide_folder()) | set(db.scalars(select(WorkshopGuidePicture.name))))


def guide_picture(db: Session, name: str) -> tuple[bytes, str]:
    stored = db.get(WorkshopGuidePicture, name)
    if stored is not None:
        return stored.content, stored.media_type
    # Only names from the folder listing are served, so a crafted path cannot reach other files.
    if name not in _guide_folder():
        raise HTTPException(status_code=404, detail="Guide picture not found")
    return (settings.WORKSHOP_GUIDE_DIR / name).read_bytes(), PICTURES[Path(name).suffix.lower()]
