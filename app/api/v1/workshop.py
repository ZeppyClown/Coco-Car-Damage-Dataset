from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopJobResponse
from app.services.workshop import create_job, get_job, update_job


def require_workshop_enabled():
    # shortcut: local demo only; add authenticated access before a workshop pilot.
    if not settings.WORKSHOP_ENABLED:
        raise HTTPException(status_code=404, detail="Workshop demo is disabled")


router = APIRouter(prefix="/workshop", dependencies=[Depends(require_workshop_enabled)])


@router.post("/jobs", response_model=WorkshopJobResponse, status_code=201)
def create_draft(draft: WorkshopDraft, db: Session = Depends(get_db)):
    return create_job(db, draft)


@router.get("/jobs/{job_id}", response_model=WorkshopJobResponse)
def read_draft(job_id: UUID, db: Session = Depends(get_db)):
    return get_job(db, job_id)


@router.patch("/jobs/{job_id}", response_model=WorkshopJobResponse)
def replace_draft(job_id: UUID, request: WorkshopDraftUpdate, db: Session = Depends(get_db)):
    return update_job(db, job_id, request)
