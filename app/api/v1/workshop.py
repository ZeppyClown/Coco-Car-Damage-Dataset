import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from uuid import UUID
from zoneinfo import ZoneInfo
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Path, Query, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask

from app.core.config import settings
from app.core.workshop_auth import BASIC
from app.db.session import get_db
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopJobResponse, WorkshopDocumentResponse, DataOrigin, RecordStage, WorkshopConfirmRequest, WorkshopRevisionResponse, WorkshopExportResponse, WorkshopExtractionRequest, WorkshopLookupResponse
from app.services.workshop_extraction import extract_source
from app.services.workshop import create_job, get_job, update_job, attach_document, get_document, document_file, MAX_UPLOAD_BYTES, confirm_job, list_revisions, generate_export, get_export, export_file, lookup_jobs
from app.schemas.workshop_invoice import InvoiceRequest, InvoiceIssueRequest, InvoicePreview, InvoiceResponse, InvoiceSettingsResponse
from app.schemas.workshop_books import CompanyRequest, ExpenseRequest, PaymentRequest, UserRequest, UserSwitch
from app.services.workshop_books import month_sheet, month_csv, payments, add_payment, vehicle_history, guide_pictures, guide_picture, expense_sheet, expense_csv, add_expense, profit_and_loss
from app.services.workshop_backup import write_backup
from app.services.workshop_setup import setup_state, save_company, add_example_data, remove_example_data, save_form, save_guide_picture, GUIDE_NAME, users, save_user, switch_user, MAX_FORM_BYTES
from app.services.workshop_sheet import job_sheet_html, invoice_sheet_html, car_outline
from app.services.workshop_invoice import billing_supplier, preview_invoice, issue_invoice, get_invoice, job_invoice, invoice_response, invoice_html


def require_workshop_enabled(request: Request):
    if not settings.WORKSHOP_ENABLED:
        raise HTTPException(status_code=404, detail="The workshop app is switched off")
    if not getattr(request.state, "workshop_user", None):
        raise HTTPException(status_code=503, detail="Workshop authentication boundary is unavailable")
    return request.state.workshop_user


def require_owner(request: Request):
    if getattr(request.state, "workshop_role", None) != "owner":
        raise HTTPException(status_code=403, detail="Only an owner login can change this. Ask the owner to do it.")
    return request.state.workshop_user


router = APIRouter(prefix="/workshop", dependencies=[Depends(BASIC), Depends(require_workshop_enabled)])


@router.post("/documents", response_model=WorkshopDocumentResponse, status_code=201)
def upload_source(file: UploadFile = File(...), data_origin: DataOrigin = Form(...), db: Session = Depends(get_db)):
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    return attach_document(db, content, file.filename or "", file.content_type or "", data_origin)


@router.get("/documents/{document_id}/preview")
def preview_source(document_id: UUID, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    return Response(
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
def create_job_download(revision_id: UUID, db: Session = Depends(get_db)):
    return generate_export(db, revision_id)


@router.get("/exports/{export_id}/download")
def download_job_file(export_id: UUID, db: Session = Depends(get_db)):
    export = get_export(db, export_id)
    return Response(
        export_file(export), media_type="text/csv; charset=utf-8",
        headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                 "Content-Disposition": f'attachment; filename="workshop-job-{export.id}.csv"'},
    )


@router.get("/revisions/{revision_id}/sheet", response_class=HTMLResponse)
def print_job_sheet(revision_id: UUID, db: Session = Depends(get_db)):
    return HTMLResponse(job_sheet_html(db, revision_id), headers=SHEET_HEADERS)


@router.get("/billing-settings", response_model=InvoiceSettingsResponse)
def billing_settings(db: Session = Depends(get_db)):
    supplier = billing_supplier(db)
    return InvoiceSettingsResponse(real_invoices_enabled=supplier is not None, supplier=supplier)


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
def car_outline_picture(db: Session = Depends(get_db)):
    return Response(car_outline(db), media_type="image/png", headers={"Cache-Control": "no-store"})


@router.get("/books")
def books(month: str = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$"), format: str = Query("json", pattern="^(json|csv)$"),
          db: Session = Depends(get_db)):
    sheet = month_sheet(db, month)
    if format == "json":
        return sheet
    return Response(month_csv(sheet), media_type="text/csv; charset=utf-8", headers={
        "Cache-Control": "no-store", "Content-Disposition": f'attachment; filename="workshop-books-{month}.csv"'})


@router.get("/invoices/{invoice_id}/payments")
def read_payments(invoice_id: UUID, db: Session = Depends(get_db)):
    return payments(db, invoice_id)


@router.post("/invoices/{invoice_id}/payments", status_code=201)
def record_payment(invoice_id: UUID, request: PaymentRequest, db: Session = Depends(get_db),
                   actor: str = Depends(require_workshop_enabled)):
    return add_payment(db, invoice_id, request, actor)


@router.get("/vehicles")
def car_history(number: str = Query(min_length=1, max_length=200), db: Session = Depends(get_db)):
    return vehicle_history(db, number)


@router.get("/guide")
def guide_list(db: Session = Depends(get_db)):
    return guide_pictures(db)


@router.get("/guide/{name}")
def guide_file(name: str, db: Session = Depends(get_db)):
    content, media_type = guide_picture(db, name)
    return Response(content, media_type=media_type, headers={"Cache-Control": "no-store"})


@router.put("/setup/guide/{name}")
def upload_guide_picture(name: str = Path(pattern=GUIDE_NAME), file: UploadFile = File(...), db: Session = Depends(get_db),
                         actor: str = Depends(require_owner)):
    return save_guide_picture(db, name, file.file.read(MAX_FORM_BYTES + 1), actor)


MONTH = Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


@router.get("/expenses")
def read_expenses(month: str = MONTH, format: str = Query("json", pattern="^(json|csv)$"), db: Session = Depends(get_db)):
    sheet = expense_sheet(db, month)
    if format == "json":
        return sheet
    return Response(expense_csv(sheet), media_type="text/csv; charset=utf-8", headers={
        "Cache-Control": "no-store", "Content-Disposition": f'attachment; filename="workshop-expenses-{month}.csv"'})


@router.post("/expenses", status_code=201)
def record_expense(request: ExpenseRequest, db: Session = Depends(get_db), actor: str = Depends(require_workshop_enabled)):
    return add_expense(db, request, actor)


@router.get("/profit")
def read_profit(month: str = MONTH, db: Session = Depends(get_db)):
    return profit_and_loss(db, month)


@router.get("/setup")
def read_setup(db: Session = Depends(get_db)):
    return setup_state(db)


@router.put("/setup")
def write_setup(request: CompanyRequest, db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return save_company(db, request, actor)


@router.post("/setup/example-jobs", status_code=201)
def example_jobs(db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return add_example_data(db, actor)


@router.get("/backup")
def download_backup(db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    """Everything in the workshop tables, photos included, as one zip file for the owner to keep."""
    handle = NamedTemporaryFile(suffix=".zip", delete=False)
    handle.close()
    try:
        write_backup(db.connection(), handle.name)
    except Exception:
        os.unlink(handle.name)
        raise
    day = datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d-%H%M")
    return FileResponse(handle.name, media_type="application/zip", filename=f"workshop-backup-{day}.zip",
                        headers={"Cache-Control": "no-store"}, background=BackgroundTask(os.unlink, handle.name))


@router.delete("/setup/example-jobs")
def drop_example_jobs(db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return remove_example_data(db)


@router.put("/setup/form")
def upload_form(file: UploadFile = File(...), db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return save_form(db, file.file.read(MAX_FORM_BYTES + 1), actor)


@router.get("/users")
def read_users(request: Request, db: Session = Depends(get_db)):
    return {"me": request.state.workshop_user, "role": request.state.workshop_role, "users": users(db) if request.state.workshop_role == "owner" else []}


@router.post("/users", status_code=201)
def write_user(request: UserRequest, db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return save_user(db, request, actor)


@router.post("/users/{username}/active")
def switch_login(username: str, request: UserSwitch, db: Session = Depends(get_db), actor: str = Depends(require_owner)):
    return switch_user(db, username, request.active)
