"""Print a reviewed record onto the workshop's own blank job sheet.

The configured blank form is the page background and reviewed values are placed
where staff would write them, so the print-out reads like the paper sheet.
"""
from base64 import b64encode
from datetime import date
from html import escape
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import WorkshopJobRevision
from app.schemas.workshop import WorkshopRevisionResponse
from app.services.workshop import _revision_response

ROWS_PER_SHEET = 20
# Positions are percentages of the blank form (yap-motor quotation/job sheet scan).
# Recalibrate here if the workshop changes its printed form.
FIRST_ROW_TOP, ROW_PITCH = 22.9, 3.1
FIELDS = {"quotation": (83, 5.6), "vehicle": (10, 9.9), "make_model": (73.5, 10.2), "owner": (9.5, 13.3),
          "date_in": (10.5, 16.4), "date_out": (42.5, 16.4)}

STYLE = """body{margin:0;background:#888;font:13px Arial,Helvetica,sans-serif;color:#0b2a6b}
.note{background:#fff3cd;color:#000;margin:0;padding:.5rem 1rem}
.sheet{position:relative;width:210mm;aspect-ratio:896/1319;margin:8px auto;background:#fff;overflow:hidden}
.sheet img{position:absolute;inset:0;width:100%;height:100%}
.sheet span{position:absolute;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:bold}
.item{left:7%;width:32.5%}.amount{left:40.3%;width:9.6%;text-align:right}
.notes{left:51.5%;top:22.5%;width:41%;white-space:pre-wrap!important;font-size:11px}
.page{right:6%;top:1.2%;font-size:10px;color:#000}
@media print{body{background:#fff}.sheet{margin:0;page-break-after:always}.screen{display:none}}
@page{size:A4;margin:0}"""


def _day(value: date | None) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def render_job_sheet(revision: WorkshopRevisionResponse, template: bytes | None) -> str:
    def e(value: object) -> str:
        return escape(str(value or ""), quote=True)

    record = revision.record
    background = ""
    if template:
        kind = "png" if template.startswith(b"\x89PNG") else "jpeg"
        background = f'<img alt="" src="data:image/{kind};base64,{b64encode(template).decode()}">'
    values = {
        "quotation": _day(record.quotation_date), "vehicle": record.vehicle_reference,
        "make_model": " ".join(filter(None, (record.make, record.model))), "owner": record.customer_reference,
        "date_in": _day(record.date_in), "date_out": _day(record.date_out),
    }
    header = "".join(f'<span style="left:{left}%;top:{top}%">{e(values[name])}</span>'
                     for name, (left, top) in FIELDS.items())
    totals = [f"{label}: {value:.2f}" for label, value in (
        ("Total", record.written_total), ("Adjustment", record.written_adjustment),
        ("Grand total", record.written_grand_total)) if value is not None]
    notes = "\n".join(filter(None, (record.diagram_notes or record.diagram_notes_raw, *totals)))
    items = list(record.items) or [None]
    pages = [items[start:start + ROWS_PER_SHEET] for start in range(0, len(items), ROWS_PER_SHEET)]
    sheets = []
    for number, rows in enumerate(pages, 1):
        cells = []
        for index, row in enumerate(filter(None, rows)):
            top = FIRST_ROW_TOP + ROW_PITCH * index
            text = f"<s>{e(row.description_raw)}</s>" if row.cancelled else e(row.description or row.description_raw)
            amount = "" if row.cancelled or row.amount is None else f"{row.amount:.2f}"
            cells.append(f'<span class="item" style="top:{top:.2f}%">{text}</span>'
                         f'<span class="amount" style="top:{top:.2f}%">{amount}</span>')
        sheets.append(f'<section class="sheet">{background}{header}{"".join(cells)}'
                      f'<span class="notes">{e(notes)}</span>'
                      f'<span class="page">Sheet {number} of {len(pages)} · {e(record.job_reference)} v{revision.version}</span></section>')
    notices = ["Use your browser's Print / Save as PDF."]
    if record.data_origin == "synthetic_demo":
        notices.insert(0, "DEMO ONLY — fictional record.")
    if not template:
        notices.append("Blank job-sheet image is not configured, so only the values are shown.")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Job sheet {e(record.job_reference)}</title>'
            f'<style>{STYLE}</style></head><body><p class="note screen">{" ".join(notices)}</p>{"".join(sheets)}</body></html>')


def job_sheet_html(db: Session, revision_id: UUID) -> str:
    revision = db.scalar(select(WorkshopJobRevision).where(WorkshopJobRevision.id == revision_id))
    if revision is None:
        raise HTTPException(status_code=404, detail="Reviewed workshop revision not found")
    template: Path | None = settings.WORKSHOP_SHEET_TEMPLATE
    try:
        # An empty WORKSHOP_SHEET_TEMPLATE= line parses as Path("."), which means "not configured".
        content = template.read_bytes() if template and template != Path(".") else None
    except OSError:
        raise HTTPException(status_code=503, detail="Configured blank job-sheet image cannot be read")
    return render_job_sheet(_revision_response(revision), content)
