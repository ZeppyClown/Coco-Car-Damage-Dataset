from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopJobResponse, WorkshopDocumentResponse, DataOrigin, RecordStage, WorkshopConfirmRequest, WorkshopRevisionResponse, WorkshopExportResponse, WorkshopExtractionRequest, WorkshopLookupResponse
from app.services.workshop_extraction import extract_source
from app.services.workshop import create_job, get_job, update_job, attach_document, get_document, document_file, MAX_UPLOAD_BYTES, confirm_job, list_revisions, generate_export, get_export, export_file, lookup_jobs


def require_workshop_enabled():
    # shortcut: local demo only; add authenticated access before a workshop pilot.
    if not settings.WORKSHOP_ENABLED:
        raise HTTPException(status_code=404, detail="Workshop demo is disabled")


router = APIRouter(prefix="/workshop", dependencies=[Depends(require_workshop_enabled)])


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
def confirm_draft(job_id: UUID, request: WorkshopConfirmRequest, db: Session = Depends(get_db)):
    return confirm_job(db, job_id, request)


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
