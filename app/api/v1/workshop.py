from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopJobResponse, WorkshopDocumentResponse, DataOrigin
from app.services.workshop import create_job, get_job, update_job, attach_document, get_document, document_file, MAX_UPLOAD_BYTES


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


@router.post("/jobs", response_model=WorkshopJobResponse, status_code=201)
def create_draft(draft: WorkshopDraft, db: Session = Depends(get_db)):
    return create_job(db, draft)


@router.get("/jobs/{job_id}", response_model=WorkshopJobResponse)
def read_draft(job_id: UUID, db: Session = Depends(get_db)):
    return get_job(db, job_id)


@router.patch("/jobs/{job_id}", response_model=WorkshopJobResponse)
def replace_draft(job_id: UUID, request: WorkshopDraftUpdate, db: Session = Depends(get_db)):
    return update_job(db, job_id, request)
