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
from app.db.models import WorkshopInvoice, WorkshopJobRevision, WorkshopPayment
from app.schemas.workshop_books import PaymentRequest
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


def guide_pictures() -> list[str]:
    folder: Path | None = settings.WORKSHOP_GUIDE_DIR
    if not folder or folder == Path(".") or not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if path.is_file() and path.suffix.lower() in PICTURES)


def guide_picture(name: str) -> tuple[Path, str]:
    # Only names from the folder listing are served, so a crafted path cannot reach other files.
    if name not in guide_pictures():
        raise HTTPException(status_code=404, detail="Guide picture not found")
    return settings.WORKSHOP_GUIDE_DIR / name, PICTURES[Path(name).suffix.lower()]
