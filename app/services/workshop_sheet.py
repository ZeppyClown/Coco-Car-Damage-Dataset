"""Print a reviewed record or issued invoice onto the workshop's own blank job sheet.

The configured blank form is the page background and reviewed values are placed
where staff would write them, so the print-out reads like the paper sheet.
"""
from base64 import b64encode
from datetime import date
from functools import lru_cache
from html import escape
from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import WorkshopJobRevision
from app.schemas.workshop import WorkshopReviewedDraft, WorkshopRevisionResponse
from app.schemas.workshop_invoice import InvoiceResponse
from app.services.workshop import _revision_response
from app.services.workshop_invoice import get_invoice, invoice_html, invoice_response

ROWS_PER_SHEET = 20
# Positions are percentages of the blank form (yap-motor quotation/job sheet scan).
# Recalibrate here if the workshop changes its printed form.
FIRST_ROW_TOP, ROW_PITCH = 22.9, 3.1
FIELDS = {"quotation": (83, 5.6), "vehicle": (10, 9.9), "make_model": (73.5, 10.2), "owner": (9.5, 13.3),
          "contact": (71.5, 13.3), "date_in": (10.5, 16.4), "date_out": (42.5, 16.4)}
TICK_TOP = 19.2
YES_NO = {"knock": (11.4, 16.5), "spray": (27, 32.3), "repair": (42.7, 47.9)}  # "Servicing" on the form
FUEL = {"empty": 68.6, "1/5": 73.9, "2/5": 79.2, "3/5": 84.4, "4/5": 89.3, "full": 94.4}
DIAGRAM = (50.5, 26, 94, 82.5)  # left, top, right, bottom of the car outline
SECTION_ORDER = {"knock": 0, "repair": 1, None: 1, "spray": 2}

STYLE = """body{margin:0;background:#888;font:13px Arial,Helvetica,sans-serif;color:#0b2a6b}
.note{background:#fff3cd;color:#000;margin:0;padding:.5rem 1rem}
.sheet{position:relative;width:210mm;aspect-ratio:896/1319;margin:8px auto;background:#fff;overflow:hidden}
.sheet img{position:absolute;inset:0;width:100%;height:100%}
.sheet span{position:absolute;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:bold}
.item{left:7%;width:32.5%}.amount{left:40.3%;width:9.6%;text-align:right}
.notes{left:51.5%;top:22.5%;width:41%;white-space:pre-wrap!important;overflow-wrap:anywhere;font-size:11px}
.page{right:6%;top:1.2%;font-size:10px;color:#000}
.tick{width:4.2%;height:1.7%;margin:-.2% 0 0 -2.1%;border:2px solid #0b2a6b;border-radius:50%}
.mark{width:2.6%;aspect-ratio:1;margin:-1.3% 0 0 -1.3%;border:2px solid #c00;border-radius:50%;color:#c00;
background:#fffc;text-align:center;font-size:11px;line-height:1.5}
.total{color:#000}.item:has(.total){text-align:right}
@media print{body{background:#fff}.sheet{margin:0;page-break-after:always}.screen{display:none}}
@page{size:A4;margin:0}"""


def _day(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def _e(value: object) -> str:
    return escape(str(value or ""), quote=True)


def _document(title: str, pages: list[str], notices: list[str], template: bytes | None) -> str:
    background = ""
    if template:
        kind = "png" if template.startswith(b"\x89PNG") else "jpeg"
        background = f'<img alt="" src="data:image/{kind};base64,{b64encode(template).decode()}">'
    else:
        notices = [*notices, "Blank job-sheet image is not configured, so only the values are shown."]
    sheets = "".join(f'<section class="sheet">{background}{page}</section>' for page in pages)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{_e(title)}</title>'
            f'<style>{STYLE}</style></head><body><p class="note screen">{" ".join(notices)}</p>{sheets}</body></html>')


def _header(record: WorkshopReviewedDraft, owner: str | None = None) -> str:
    values = {
        "quotation": _day(record.quotation_date), "vehicle": record.vehicle_reference,
        "make_model": " ".join(filter(None, (record.make, record.model))),
        "owner": owner or record.customer_reference, "contact": record.contact,
        "date_in": _day(record.date_in), "date_out": _day(record.date_out),
    }
    used = {item.section for item in record.items if not item.cancelled}
    ticks = [positions[0 if section in used else 1] for section, positions in YES_NO.items()]
    if record.fuel_level:
        ticks.append(FUEL[record.fuel_level])
    left, top, right, bottom = DIAGRAM
    marks = "".join(
        f'<span class="mark" style="left:{left + mark.x * (right - left) / 100:.2f}%;'
        f'top:{top + mark.y * (bottom - top) / 100:.2f}%">{number}</span>'
        for number, mark in enumerate(record.diagram_marks, 1))
    return "".join(f'<span style="left:{left}%;top:{top}%">{_e(values[name])}</span>'
                   for name, (left, top) in FIELDS.items()) + "".join(
        f'<span class="tick" style="left:{left}%;top:{TICK_TOP}%"></span>' for left in ticks) + marks


def _mark_notes(record: WorkshopReviewedDraft) -> list[str]:
    return [f"{number} {mark.note}" for number, mark in enumerate(record.diagram_marks, 1) if mark.note]


CLAIMS = {"own_damage": "own damage claim", "third_party": "third-party claim", "private_settlement": "private settlement",
          "report_only": "report only"}


def _accident_note(record: WorkshopReviewedDraft) -> str | None:
    accident = record.accident
    if accident is None:
        return None
    return " · ".join(filter(None, ("Accident: " + CLAIMS[accident.claim_type], accident.insurer, accident.report_number,
                                    accident.excess is not None and f"excess {accident.excess:.2f}")))


def _row(index: int, text: str, amount: str) -> str:
    top = FIRST_ROW_TOP + ROW_PITCH * index
    return (f'<span class="item" style="top:{top:.2f}%">{text}</span>'
            f'<span class="amount" style="top:{top:.2f}%">{amount}</span>')


PRINT_HINT = ["Use your browser's Print / Save as PDF."]


def render_job_sheet(revision: WorkshopRevisionResponse, template: bytes | None) -> str:
    record = revision.record
    totals = [f"{label}: {value:.2f}" for label, value in (
        ("Total", record.written_total), ("Adjustment", record.written_adjustment),
        ("Grand total", record.written_grand_total)) if value is not None]
    notes = "\n".join(filter(None, (record.diagram_notes or record.diagram_notes_raw, _accident_note(record), *_mark_notes(record), *totals)))
    items = sorted(record.items, key=lambda item: SECTION_ORDER[item.section]) or [None]
    chunks = [items[start:start + ROWS_PER_SHEET] for start in range(0, len(items), ROWS_PER_SHEET)]
    pages = []
    for number, rows in enumerate(chunks, 1):
        cells = "".join(_row(
            index, f"<s>{_e(row.description_raw)}</s>" if row.cancelled else _e(row.description or row.description_raw),
            "" if row.cancelled or row.amount is None else f"{row.amount:.2f}",
        ) for index, row in enumerate(filter(None, rows)))
        pages.append(f'{_header(record)}{cells}<span class="notes">{_e(notes)}</span>'
                     f'<span class="page">Sheet {number} of {len(chunks)} · {_e(record.job_reference)} v{revision.version}</span>')
    return _document(f"Job sheet {record.job_reference}", pages, PRINT_HINT, template)


def render_invoice_sheet(invoice: InvoiceResponse, record: WorkshopReviewedDraft, template: bytes | None) -> str:
    """The issued invoice on the same form: work lines, then the totals in the last rows."""
    preview, request = invoice.preview, invoice.preview.request
    registered = request.supplier.gst_status == "registered"
    totals = [("TOTAL", preview.net), ("GST 9%", preview.gst), ("GRAND TOTAL", preview.total)] if registered \
        else [("GRAND TOTAL", preview.total)]
    if request.discount:
        totals.insert(0, ("LESS DISCOUNT", request.discount))
    room = ROWS_PER_SHEET - len(totals)
    lines = list(preview.lines)
    chunks = [lines[start:start + ROWS_PER_SHEET] for start in range(0, len(lines), ROWS_PER_SHEET)] or [[]]
    if len(chunks[-1]) > room:
        chunks.append([])
    title = "TAX INVOICE" if registered else "INVOICE"
    basis = f"Prices are GST-{request.pricing_basis}." if registered else "No GST charged."
    notes = "\n".join(filter(None, (
        title, f"No: {invoice.number}", f"Date: {_day(request.invoice_date)}", basis,
        f"Issued by {invoice.issued_by}", record.diagram_notes, *_mark_notes(record))))
    pages = []
    for number, rows in enumerate(chunks, 1):
        cells = "".join(_row(index, _e(line.description), f"{line.amount:.2f}") for index, line in enumerate(rows))
        if number == len(chunks):
            cells += "".join(_row(room + index, f'<b class="total">{label}</b>', f"{amount:.2f}")
                             for index, (label, amount) in enumerate(totals))
        pages.append(f'{_header(record, request.customer.name)}{cells}<span class="notes">{_e(notes)}</span>'
                     f'<span class="page">Sheet {number} of {len(chunks)} · {_e(preview.job_reference)}</span>')
    return _document(f"{invoice.number} — {title}", pages, PRINT_HINT, template)


def _template() -> bytes | None:
    template: Path | None = settings.WORKSHOP_SHEET_TEMPLATE
    try:
        # An empty WORKSHOP_SHEET_TEMPLATE= line parses as Path("."), which means "not configured".
        return template.read_bytes() if template and template != Path(".") else None
    except OSError:
        raise HTTPException(status_code=503, detail="Configured blank job-sheet image cannot be read")


@lru_cache(maxsize=2)
def _outline(path: Path, modified: float) -> bytes:
    with Image.open(path) as form:
        left, top, right, bottom = DIAGRAM
        box = (round(form.width * left / 100), round(form.height * top / 100),
               round(form.width * right / 100), round(form.height * bottom / 100))
        output = BytesIO()
        form.convert("RGB").crop(box).save(output, "PNG")
        return output.getvalue()


def car_outline() -> bytes:
    """The car drawing cut from the configured form, for marking damage on screen."""
    template: Path | None = settings.WORKSHOP_SHEET_TEMPLATE
    if not template or template == Path("."):
        raise HTTPException(status_code=404, detail="Blank job-sheet image is not configured")
    try:
        return _outline(template, template.stat().st_mtime)
    except (OSError, ValueError):
        raise HTTPException(status_code=503, detail="Configured blank job-sheet image cannot be read")


def _revision(db: Session, revision_id: UUID) -> WorkshopRevisionResponse:
    revision = db.scalar(select(WorkshopJobRevision).where(WorkshopJobRevision.id == revision_id))
    if revision is None:
        raise HTTPException(status_code=404, detail="Reviewed workshop revision not found")
    return _revision_response(revision)


def job_sheet_html(db: Session, revision_id: UUID) -> str:
    return render_job_sheet(_revision(db, revision_id), _template())


def invoice_sheet_html(db: Session, invoice_id: UUID) -> str:
    invoice = get_invoice(db, invoice_id)
    invoice_html(invoice)  # refuse to restyle an invoice whose stored copy fails its integrity check
    response = invoice_response(invoice)
    return render_invoice_sheet(response, _revision(db, response.preview.revision_id).record, _template())
