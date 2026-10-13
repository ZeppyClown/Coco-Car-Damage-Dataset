from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.workshop_auth import BASIC
from app.db.session import get_db
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopJobResponse, WorkshopDocumentResponse, DataOrigin, RecordStage, WorkshopConfirmRequest, WorkshopRevisionResponse, WorkshopExportResponse, WorkshopExtractionRequest, WorkshopLookupResponse
from app.services.workshop_extraction import extract_source
from app.services.workshop import create_job, get_job, update_job, attach_document, get_document, document_file, MAX_UPLOAD_BYTES, confirm_job, list_revisions, generate_export, get_export, export_file, lookup_jobs
from app.schemas.workshop_invoice import InvoiceRequest, InvoiceIssueRequest, InvoicePreview, InvoiceResponse, InvoiceSettingsResponse
from app.services.workshop_sheet import job_sheet_html, invoice_sheet_html, car_outline
from app.services.workshop_invoice import preview_invoice, issue_invoice, get_invoice, job_invoice, invoice_response, invoice_html


def require_workshop_enabled(request: Request):
    if not settings.WORKSHOP_ENABLED:
        raise HTTPException(status_code=404, detail="Workshop demo is disabled")
    if not getattr(request.state, "workshop_user", None):
        raise HTTPException(status_code=503, detail="Workshop authentication boundary is unavailable")
    return request.state.workshop_user


router = APIRouter(prefix="/workshop", dependencies=[Depends(BASIC), Depends(require_workshop_enabled)])


@router.post("/documents", response_model=WorkshopDocumentResponse, status_code=201)
def upload_source(file: UploadFile = File(...), data_origin: DataOrigin = Form(...), db: Session = Depends(get_db)):
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    return attach_document(db, content, file.filename or "", file.content_type or "", data_origin)


@router.get("/documents/{document_id}/preview")
def preview_source(document_id: UUID, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    return FileResponse(
        document_file(document), media_type=document.media_type,
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/documents/{document_id}/extract", response_model=WorkshopDraft)
def propose_source_fields(document_id: UUID, request: WorkshopExtractionRequest, db: Session = Depends(get_db)):
    return extract_source(db, document_id)


@router.post("/jobs", response_model=WorkshopJobResponse, status_code=201)
def create_draft(draft: WorkshopDraft, db: Session = Depends(get_db)):
    return create_job(db, draft)


@router.get("/jobs", response_model=WorkshopLookupResponse)
def find_reviewed_jobs(
    q: str | None = Query(None, max_length=200), job_id: UUID | None = None,
    customer: str | None = Query(None, max_length=200), vehicle: str | None = Query(None, max_length=200),
    reference: str | None = Query(None, max_length=200), stage: RecordStage | None = None,
    reviewed_from: date | None = None, reviewed_to: date | None = None,
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db),
):
    return lookup_jobs(db, q=q, job_id=job_id, customer=customer, vehicle=vehicle, reference=reference,
                       stage=stage, reviewed_from=reviewed_from, reviewed_to=reviewed_to, limit=limit, offset=offset)


@router.get("/jobs/{job_id}", response_model=WorkshopJobResponse)
def read_draft(job_id: UUID, db: Session = Depends(get_db)):
    return get_job(db, job_id)


@router.patch("/jobs/{job_id}", response_model=WorkshopJobResponse)
def replace_draft(job_id: UUID, request: WorkshopDraftUpdate, db: Session = Depends(get_db)):
    return update_job(db, job_id, request)


@router.post("/jobs/{job_id}/confirm", response_model=WorkshopRevisionResponse)
def confirm_draft(job_id: UUID, request: WorkshopConfirmRequest, db: Session = Depends(get_db), reviewer: str = Depends(require_workshop_enabled)):
    return confirm_job(db, job_id, request.model_copy(update={"reviewer":reviewer}), authenticated=True)


@router.get("/jobs/{job_id}/revisions", response_model=list[WorkshopRevisionResponse])
def read_revisions(job_id: UUID, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    return list_revisions(db, job_id, limit, offset)


@router.post("/revisions/{revision_id}/exports", response_model=WorkshopExportResponse)
def create_demo_export(revision_id: UUID, db: Session = Depends(get_db)):
    return generate_export(db, revision_id)


@router.get("/exports/{export_id}/download")
def download_demo_export(export_id: UUID, db: Session = Depends(get_db)):
    export = get_export(db, export_id)
    return FileResponse(
        export_file(export), media_type="text/csv; charset=utf-8", filename=f"workshop-demo-{export.id}.csv",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
    )


@router.get("/revisions/{revision_id}/sheet", response_class=HTMLResponse)
def print_job_sheet(revision_id: UUID, db: Session = Depends(get_db)):
    return HTMLResponse(job_sheet_html(db, revision_id), headers=SHEET_HEADERS)


@router.get("/billing-settings", response_model=InvoiceSettingsResponse)
def billing_settings():
    return InvoiceSettingsResponse(real_invoices_enabled=settings.WORKSHOP_REAL_INVOICES_ENABLED,
                                   supplier=settings.WORKSHOP_BILLING_SUPPLIER)


@router.post("/revisions/{revision_id}/invoice-preview", response_model=InvoicePreview)
def calculate_bill(revision_id: UUID, request: InvoiceRequest, db: Session = Depends(get_db)):
    return preview_invoice(db, revision_id, request)


@router.post("/revisions/{revision_id}/invoice", response_model=InvoiceResponse)
def issue_bill(revision_id: UUID, request: InvoiceIssueRequest, db: Session = Depends(get_db), actor: str = Depends(require_workshop_enabled)):
    return issue_invoice(db, revision_id, request.invoice, actor)


@router.get("/jobs/{job_id}/invoice", response_model=InvoiceResponse)
def read_job_bill(job_id: UUID, db: Session = Depends(get_db)):
    return job_invoice(db, job_id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def read_bill(invoice_id: UUID, db: Session = Depends(get_db)):
    return invoice_response(get_invoice(db, invoice_id))


@router.get("/invoices/{invoice_id}/print", response_class=HTMLResponse)
def print_bill(invoice_id: UUID, db: Session = Depends(get_db)):
    return HTMLResponse(invoice_html(get_invoice(db, invoice_id)), headers={
        "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'",
    })


SHEET_HEADERS = {
    "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
    "Content-Security-Policy": "default-src 'none'; img-src data:; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'",
}


@router.get("/invoices/{invoice_id}/sheet", response_class=HTMLResponse)
def print_bill_on_form(invoice_id: UUID, db: Session = Depends(get_db)):
    return HTMLResponse(invoice_sheet_html(db, invoice_id), headers=SHEET_HEADERS)


@router.get("/sheet-diagram")
def car_outline_picture():
    return Response(car_outline(), media_type="image/png", headers={"Cache-Control": "no-store"})
