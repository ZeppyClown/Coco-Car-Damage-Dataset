"""Deterministic billing: subtotal rounding and one immutable invoice per job."""
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from html import escape
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import WorkshopJob, WorkshopJobRevision, WorkshopInvoice
from app.schemas.workshop import WorkshopReviewedDraft
from app.schemas.workshop_invoice import InvoiceRequest, InvoicePreview, InvoiceResponse


CENT = Decimal("0.01")
RATE = Decimal("0.09")


def calculate_invoice(revision: WorkshopJobRevision, request: InvoiceRequest) -> InvoicePreview:
    if request.invoice_date < date(2024, 1, 1):
        raise HTTPException(422, "This module supports the current GST rate only, from 1 January 2024")
    record = WorkshopReviewedDraft.model_validate(revision.record)
    if record.record_stage != "completed_work":
        raise HTTPException(422, "Invoice requires reviewed completed work; a quote is not billable work")
    if record.currency != "SGD":
        raise HTTPException(422, "Invoices support SGD only")
    active = [item for item in record.items if not item.cancelled]
    if any(item.amount is None or item.amount_state != "confirmed" for item in active):
        raise HTTPException(422, "Every billed item needs a confirmed price; unknown is not zero")
    subtotal = sum((item.amount for item in active), Decimal("0.00"))
    if subtotal >= Decimal("10000000000") or request.discount > subtotal:
        raise HTTPException(422, "Invoice subtotal is too large or discount exceeds the subtotal")
    taxable = subtotal - request.discount
    registered = request.supplier.gst_status == "registered"
    # One fixed subtotal method; never sum individually rounded line taxes.
    gst = Decimal("0.00")
    if registered:
        gst = (taxable * RATE / (1 + RATE) if request.pricing_basis == "inclusive"
               else taxable * RATE).quantize(CENT, rounding=ROUND_HALF_UP)
    net = taxable - gst if registered and request.pricing_basis == "inclusive" else taxable
    total = net + gst
    if total >= Decimal("10000000000"):
        raise HTTPException(422, "Invoice total is too large")
    return InvoicePreview(
        job_id=revision.job_id, revision_id=revision.id, data_origin=record.data_origin,
        job_reference=record.job_reference, vehicle_reference=record.vehicle_reference,
        request=request, lines=[{"description": item.description, "amount": item.amount} for item in active],
        subtotal=subtotal, net=net, gst=gst, total=total,
        gst_rate="9%" if registered else "not_applicable",
    )


def preview_invoice(db: Session, revision_id: UUID, request: InvoiceRequest) -> InvoicePreview:
    revision = db.get(WorkshopJobRevision, revision_id)
    if revision is None:
        raise HTTPException(404, "Reviewed workshop revision not found")
    return calculate_invoice(revision, request)


def invoice_response(invoice: WorkshopInvoice) -> InvoiceResponse:
    issued_at = invoice.issued_at
    if issued_at.tzinfo is None:
        issued_at = issued_at.replace(tzinfo=timezone.utc)
    issued_at = issued_at.astimezone(timezone.utc)
    return InvoiceResponse(id=invoice.id, number=invoice.number, preview=invoice.snapshot,
                           issued_by=invoice.issued_by, issued_at=issued_at, checksum=invoice.checksum)


def get_invoice(db: Session, invoice_id: UUID) -> WorkshopInvoice:
    invoice = db.get(WorkshopInvoice, invoice_id)
    if invoice is None:
        raise HTTPException(404, "Workshop invoice not found")
    return invoice


def job_invoice(db: Session, job_id: UUID) -> InvoiceResponse:
    invoice = db.scalar(select(WorkshopInvoice).where(WorkshopInvoice.job_id == job_id))
    if invoice is None:
        raise HTTPException(404, "No invoice issued for this job")
    return invoice_response(invoice)


def invoice_html(invoice: WorkshopInvoice) -> str:
    if sha256(invoice.html.encode("utf-8")).hexdigest() != invoice.checksum:
        raise HTTPException(503, "Stored invoice failed its integrity check")
    return invoice.html


def render_invoice(number: str, preview: InvoicePreview, actor: str, issued_at: datetime) -> str:
    def e(value):
        return escape(str(value), quote=True)
    req = preview.request
    registered = req.supplier.gst_status == "registered"
    title = "Tax Invoice" if registered else "Invoice"
    notice = "DEMO ONLY — fictional invoice, not for payment or tax claims." if preview.data_origin == "synthetic_demo" else "Issued invoice — not a payment receipt."
    lines = "".join(f"<tr><td>{e(line.description)}</td><td>{line.amount:.2f}</td></tr>" for line in preview.lines)
    gst_label = "GST @ 9%" if registered else "GST not applicable (supplier not GST-registered)"
    gst_number = f"<p>GST registration number: {e(req.supplier.gst_registration_number)}</p>" if registered else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(number)} — {title}</title>
<style>body{{font:16px system-ui;max-width:850px;margin:2rem auto;padding:1rem;color:#20343c}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:.6rem;border-bottom:1px solid #ccc;text-align:left}}
td:last-child,th:last-child{{text-align:right}}p,td{{white-space:pre-wrap;overflow-wrap:anywhere}}
.notice{{border:2px solid #b67913;padding:1rem}}@media print{{body{{margin:0;max-width:none}}.print-hint{{display:none}}}}</style></head>
<body><p class="notice">{notice}</p><h1>{title}</h1><p class="print-hint">Use your browser's Print / Save as PDF.</p>
<h2>{e(req.supplier.name)}</h2><p>{e(req.supplier.address)}</p>{gst_number}
<p>Invoice number: {e(number)}<br>Invoice date: {req.invoice_date.isoformat()}<br>Currency: SGD</p>
<h2>Bill to</h2><p>{e(req.customer.name)}<br>{e(req.customer.address)}</p>
<p>Job reference: {e(preview.job_reference)}<br>Vehicle reference: {e(preview.vehicle_reference or 'Not supplied')}</p>
<p>Line prices: GST-{req.pricing_basis if registered else 'not-applicable'}. Each amount is the captured line total.</p>
<table><thead><tr><th>Description</th><th>Line amount (SGD)</th></tr></thead><tbody>{lines}</tbody></table>
<p>Subtotal ({req.pricing_basis if registered else 'no GST'}): SGD {preview.subtotal:.2f}<br>
Discount (same price basis): SGD {req.discount:.2f}<br>
Total excluding GST: SGD {preview.net:.2f}<br>{gst_label}: SGD {preview.gst:.2f}<br>
<strong>Total payable: SGD {preview.total:.2f}</strong></p>
<p>{'Price payable includes GST.' if registered else 'No GST charged.'} GST is rounded once on the invoice subtotal to the nearest cent.</p>
<p>Issued by: {e(actor)}<br>Issued at (UTC): {issued_at.isoformat()}<br>
Job ID: {preview.job_id}<br>Reviewed revision: {preview.revision_id}<br>Calculation: {preview.calculation_version}</p>
</body></html>"""


def issue_invoice(db: Session, revision_id: UUID, request: InvoiceRequest, actor: str) -> InvoiceResponse:
    try:
        revision = db.get(WorkshopJobRevision, revision_id)
        if revision is None:
            raise HTTPException(404, "Reviewed workshop revision not found")
        # Use the draft's lock too: saving/reviewing cannot race invoice issuance.
        job = db.scalar(select(WorkshopJob).where(WorkshopJob.id == revision.job_id)
                        .with_for_update().execution_options(populate_existing=True))
        if revision.record["data_origin"] == "private_source":
            if not settings.WORKSHOP_REAL_INVOICES_ENABLED:
                raise HTTPException(403, "Real invoice issuance is disabled pending company billing settings")
            if settings.WORKSHOP_BILLING_SUPPLIER is None:
                raise HTTPException(503, "Configure the verified company billing supplier before real issuance")
            if request.supplier != settings.WORKSHOP_BILLING_SUPPLIER:
                raise HTTPException(422, "Supplier must match the configured company billing profile")
        existing = db.scalar(select(WorkshopInvoice).where(WorkshopInvoice.job_id == job.id))
        if existing is not None:
            if existing.revision_id != revision_id or existing.snapshot["request"] != request.model_dump(mode="json"):
                raise HTTPException(409, "This job already has an invoice; issued invoices cannot be replaced or billed again")
            invoice_html(existing)
            response = invoice_response(existing)
            db.commit()
            return response
        if job.draft_version != revision.version:
            raise HTTPException(409, "Review the current saved draft before invoicing; this revision is stale")
        today = datetime.now(ZoneInfo("Asia/Singapore")).date()
        if request.invoice_date != today:
            raise HTTPException(422, "Issuance uses today's Singapore date; backdated or future invoices are unsupported")
        preview = calculate_invoice(revision, request)
        invoice_id = uuid4()
        number = ("DEMO-INV-" if preview.data_origin == "synthetic_demo" else "INV-") + invoice_id.hex.upper()
        issued_at = datetime.now(timezone.utc)
        html = render_invoice(number, preview, actor, issued_at)
        invoice = WorkshopInvoice(id=invoice_id, job_id=job.id, revision_id=revision_id, number=number,
                                  snapshot=preview.model_dump(mode="json"), issued_by=actor, issued_at=issued_at,
                                  html=html, checksum=sha256(html.encode("utf-8")).hexdigest())
        db.add(invoice)
        db.flush()
        response = invoice_response(invoice)
        db.commit()
        return response
    except (SQLAlchemyError, HTTPException):
        db.rollback()
        raise
